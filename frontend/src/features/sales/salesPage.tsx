
import { useMemo, useState } from 'react'
import {
  Minus,
  Plus,
  Search,
  ShoppingCart,
  Trash2,
  Package,
  ArrowLeft,
  CheckCircle,
  LoaderCircle,
} from 'lucide-react'
import { isAxiosError } from 'axios'

import { useProducts } from '../products/hooks/useProducts'
import { useProductPackaging } from '../inventory/hooks/usePackaging'
import {
  useCreateSale,
  useAddSaleItem,
  useAddSalePayment,
  useCompleteSale,
} from './hooks/useSales'
import { salesService } from './api/sales.service'

import type { Product } from '../products/product.types'
import type { ProductPackaging } from '../inventory/packaging.types'
import type {
  PricingType,
  Sale,
  PaymentMethod,
} from './sales.types'

interface CartItem {
  product: Product
  packaging: ProductPackaging | null
  pricingType: PricingType
  quantity: number
  unitPrice: number
  packagePrice: number
  total: number
}

type PaymentMode = 'CASH' | 'MPESA' | 'SPLIT'

interface PaymentPlan {
  cash: number
  mpesa: number
  reference: string
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

function money(value: number | string) {
  return Number(Number(value).toFixed(2))
}

function getErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const data = error.response?.data

    if (typeof data === 'string') return data
    if (data?.detail) return String(data.detail)

    if (data && typeof data === 'object') {
      return Object.values(data)
        .flatMap((value) => Array.isArray(value) ? value : [value])
        .map(String)
        .join(' ')
    }

    return error.message
  }

  return error instanceof Error ? error.message : 'Something went wrong.'
}

function getPaidAmount(sale: Sale) {
  return money(
    sale.payments.reduce(
      (total, payment) => total + Number(payment.amount),
      0,
    ),
  )
}

export default function SalesPage() {
  const { data: productsData, isLoading, isError } = useProducts()
  const products = useMemo(
  () => productsData?.results ?? [],
  [productsData?.results],
)

  const createSale = useCreateSale()
  const addSaleItem = useAddSaleItem()
  const addSalePayment = useAddSalePayment()
  const completeSale = useCompleteSale()

  const [search, setSearch] = useState('')
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [pricingType, setPricingType] = useState<PricingType>('RETAIL')
  const [selectedPackagingId, setSelectedPackagingId] = useState<number | null>(null)
  const [quantity, setQuantity] = useState(1)
  const [cart, setCart] = useState<CartItem[]>([])

  const [draftSale, setDraftSale] = useState<Sale | null>(null)
  const [itemsAdded, setItemsAdded] = useState(0)
  const [checkoutStep, setCheckoutStep] = useState<'cart' | 'payment' | 'completed'>('cart')
  const [completedSale, setCompletedSale] = useState<Sale | null>(null)

  const [paymentMode, setPaymentMode] = useState<PaymentMode>('CASH')
  const [cashAmount, setCashAmount] = useState('')
  const [mpesaAmount, setMpesaAmount] = useState('')
  const [mpesaReference, setMpesaReference] = useState('')
  const [paymentPlan, setPaymentPlan] = useState<PaymentPlan | null>(null)

  const [checkoutError, setCheckoutError] = useState('')
  const [isPreparing, setIsPreparing] = useState(false)
  const [isPaying, setIsPaying] = useState(false)

  const {
    data: packagingData,
    isLoading: packagingLoading,
  } = useProductPackaging(selectedProduct?.id ?? 0)

  const packagingOptions = (packagingData?.results ?? []).filter(
    (item) => item.is_active && item.sales_enabled,
  )

  const selectedPackaging =
    packagingOptions.find((item) => item.id === selectedPackagingId) ?? null

  const filteredProducts = useMemo(() => {
    const term = search.trim().toLowerCase()

    return products.filter((product) => {
      if (!product.is_active) return false

      return (
        !term ||
        product.name.toLowerCase().includes(term) ||
        product.sku.toLowerCase().includes(term) ||
        product.brand.toLowerCase().includes(term)
      )
    })
  }, [products, search])

  const unitPrice = selectedProduct
    ? Number(
        pricingType === 'RETAIL'
          ? selectedProduct.retail_price
          : selectedProduct.wholesale_price,
      )
    : 0

  const conversionFactor = selectedPackaging?.conversion_factor ?? 1
  const packagePrice = unitPrice * conversionFactor

  const selectedBaseQuantity = quantity * conversionFactor

  const canUseWholesale = selectedProduct
    ? selectedBaseQuantity >= selectedProduct.wholesale_min_quantity
    : false

  const cartTotal = money(cart.reduce((sum, item) => sum + item.total, 0))
  const cartUnits = cart.reduce(
    (sum, item) =>
      sum + item.quantity * (item.packaging?.conversion_factor ?? 1),
    0,
  )

  const outstanding = draftSale
    ? money(Number(draftSale.total_amount) - getPaidAmount(draftSale))
    : 0

  const checkoutLocked = Boolean(draftSale) || isPreparing || checkoutStep !== 'cart'

  function selectProduct(product: Product) {
    if (checkoutLocked) return

    setSelectedProduct(product)
    setPricingType('RETAIL')
    setSelectedPackagingId(null)
    setQuantity(1)
  }

  function addToCart() {
    if (
      checkoutLocked ||
      !selectedProduct ||
      quantity < 1 ||
      !Number.isInteger(quantity)
    ) return

    const total = money(packagePrice * quantity)

    const newItem: CartItem = {
      product: selectedProduct,
      packaging: selectedPackaging,
      pricingType,
      quantity,
      unitPrice,
      packagePrice,
      total,
    }

    setCart((current) => [...current, newItem])
    setSelectedProduct(null)
    setSelectedPackagingId(null)
    setQuantity(1)
  }

  function updateCartQuantity(index: number, change: number) {
    if (checkoutLocked) return

    setCart((current) =>
      current.map((item, itemIndex) => {
        if (itemIndex !== index) return item

        const nextQuantity = item.quantity + change

        if (nextQuantity < 1) return item

        const conversionFactor =
          item.packaging?.conversion_factor ?? 1

        const nextBaseQuantity = nextQuantity * conversionFactor

        const nextPricingType: PricingType =
          item.pricingType === 'WHOLESALE' &&
          nextBaseQuantity < item.product.wholesale_min_quantity
            ? 'RETAIL'
            : item.pricingType

        const nextUnitPrice = Number(
          nextPricingType === 'WHOLESALE'
            ? item.product.wholesale_price
            : item.product.retail_price,
        )

        const nextPackagePrice = money(
          nextUnitPrice * conversionFactor,
        )

        return {
          ...item,
          pricingType: nextPricingType,
          quantity: nextQuantity,
          unitPrice: nextUnitPrice,
          packagePrice: nextPackagePrice,
          total: money(nextPackagePrice * nextQuantity),
        }
      }),
    )
  }

  function removeCartItem(index: number) {
    if (checkoutLocked) return
    setCart((current) => current.filter((_, itemIndex) => itemIndex !== index))
  }

  async function handlePrepareSale() {
    if (isPreparing || cart.length === 0) return

    setIsPreparing(true)
    setCheckoutError('')

    try {
      let sale = draftSale

      // Create the draft only once.
      if (!sale) {
        sale = await createSale.mutateAsync()
        setDraftSale(sale)
        setItemsAdded(0)
      }

      // Continue from the number of items already recorded.
      let addedCount = Math.max(itemsAdded, sale.items.length)

      for (let index = addedCount; index < cart.length; index++) {
        const item = cart[index]

        sale = await addSaleItem.mutateAsync({
          saleId: sale.id,
          payload: {
            product: item.product.id,
            pricing_type: item.pricingType,
            quantity: item.quantity,
            ...(item.packaging
              ? { packaging: item.packaging.id }
              : {}),
          },
        })

        addedCount = index + 1
        setDraftSale(sale)
        setItemsAdded(addedCount)
      }

      // Fetch the final draft before opening payment.
      sale = await salesService.getSale(sale.id)
      setDraftSale(sale)
      setItemsAdded(sale.items.length)

      setCashAmount(money(Number(sale.total_amount) - getPaidAmount(sale)).toFixed(2))
      setMpesaAmount('')
      setCheckoutStep('payment')
    } catch (error) {
      setCheckoutError(getErrorMessage(error))

      // Reconcile the draft in case an item was saved but its
      // response did not reach the browser.
      if (draftSale) {
        try {
          const refreshed = await salesService.getSale(draftSale.id)
          setDraftSale(refreshed)
          setItemsAdded(refreshed.items.length)
        } catch {
          // Keep the last known draft state.
        }
      }
    } finally {
      setIsPreparing(false)
    }
  }

  function buildPaymentPlan(): PaymentPlan | null {
    if (paymentPlan) return paymentPlan

    const cash = paymentMode === 'MPESA' ? 0 : money(Number(cashAmount) || 0)
    const mpesa = paymentMode === 'CASH' ? 0 : money(Number(mpesaAmount) || 0)
    const reference = mpesaReference.trim()

    if (cash < 0 || mpesa < 0) {
      setCheckoutError('Payment amounts cannot be negative.')
      return null
    }

    if (cash + mpesa <= 0) {
      setCheckoutError('Enter a payment amount.')
      return null
    }

    if (money(cash + mpesa) !== outstanding) {
      setCheckoutError(
        `Payments must equal the outstanding balance of ${formatCurrency(outstanding)}.`,
      )
      return null
    }

    if (mpesa > 0 && !reference) {
      setCheckoutError('Enter the M-Pesa transaction reference.')
      return null
    }

    if (mpesa === 0 && paymentMode === 'SPLIT' && cash <= 0) {
      setCheckoutError('Enter a valid split payment.')
      return null
    }

    return { cash, mpesa, reference }
  }

  async function handleConfirmPayment() {
    if (!draftSale || isPaying) return

    setIsPaying(true)
    setCheckoutError('')

    try {
      const plan = buildPaymentPlan()
      if (!plan) return

      setPaymentPlan(plan)

      // Use the latest known payment records to avoid repeating
      // a payment that the server already accepted.
      let sale = await salesService.getSale(draftSale.id)
      setDraftSale(sale)

      const recordedCash = money(
        sale.payments
          .filter((payment) => payment.payment_method === 'CASH')
          .reduce((sum, payment) => sum + Number(payment.amount), 0),
      )

      const recordedMpesa = money(
        sale.payments
          .filter((payment) => payment.payment_method === 'MPESA')
          .reduce((sum, payment) => sum + Number(payment.amount), 0),
      )

      const remainingCash = money(plan.cash - recordedCash)
      const remainingMpesa = money(plan.mpesa - recordedMpesa)

      if (remainingCash < 0 || remainingMpesa < 0) {
        throw new Error(
          'Recorded payments do not match the current payment plan. Please contact the Owner before proceeding.',
        )
      }

      if (remainingCash > 0) {
        sale = await addSalePayment.mutateAsync({
          saleId: sale.id,
          payload: {
            payment_method: 'CASH' as PaymentMethod,
            amount: remainingCash.toFixed(2),
          },
        })
        setDraftSale(sale)
      }

      if (remainingMpesa > 0) {
        sale = await addSalePayment.mutateAsync({
          saleId: sale.id,
          payload: {
            payment_method: 'MPESA' as PaymentMethod,
            amount: remainingMpesa.toFixed(2),
            reference: plan.reference,
          },
        })
        setDraftSale(sale)
      }

      // Reconcile once more before completing the transaction.
      sale = await salesService.getSale(sale.id)
      setDraftSale(sale)

      if (getPaidAmount(sale) !== money(Number(sale.total_amount))) {
        throw new Error('The sale is not fully paid. Please check the payment records.')
      }

      const completed = await completeSale.mutateAsync(sale.id)

      setCompletedSale(completed)
      setDraftSale(completed)
      setCheckoutStep('completed')
      setCheckoutError('')
      setCart([])
      setSelectedProduct(null)
      setPaymentPlan(null)
    } catch (error) {
      setCheckoutError(getErrorMessage(error))

      // Always reload after a payment/completion error.
      // This prevents duplicate payment submissions on retry.
      try {
        const refreshed = await salesService.getSale(draftSale.id)
        setDraftSale(refreshed)

        if (getPaidAmount(refreshed) === money(Number(refreshed.total_amount))) {
          setPaymentPlan((current) => current ?? {
            cash: money(
              refreshed.payments
                .filter((payment) => payment.payment_method === 'CASH')
                .reduce((sum, payment) => sum + Number(payment.amount), 0),
            ),
            mpesa: money(
              refreshed.payments
                .filter((payment) => payment.payment_method === 'MPESA')
                .reduce((sum, payment) => sum + Number(payment.amount), 0),
            ),
            reference: refreshed.payments.find(
              (payment) => payment.payment_method === 'MPESA',
            )?.reference ?? '',
          })
        } else if (refreshed.payments.length === 0) {
          setPaymentPlan(null)
        }
      } catch {
        // Keep the last known sale state if the server is unreachable.
      }
    } finally {
      setIsPaying(false)
    }
  }

  function startNewSale() {
    setDraftSale(null)
    setItemsAdded(0)
    setCompletedSale(null)
    setCheckoutStep('cart')
    setPaymentPlan(null)
    setPaymentMode('CASH')
    setCashAmount('')
    setMpesaAmount('')
    setMpesaReference('')
    setCheckoutError('')
    setCart([])
    setSelectedProduct(null)
    setSelectedPackagingId(null)
    setQuantity(1)
  }

  return (
    <main className="sales-page">
      <header className="sales-page-header">
        <div>
          <p className="dashboard-eyebrow">POINT OF SALE</p>
          <h1>
            {checkoutStep === 'completed'
              ? 'Sale completed'
              : checkoutStep === 'payment'
                ? 'Receive payment'
                : 'New Sale'}
          </h1>
          <p className="dashboard-subtitle">
            {checkoutStep === 'completed'
              ? 'The transaction has been completed successfully.'
              : checkoutStep === 'payment'
                ? 'Record the customer payment to complete this sale.'
                : 'Select products, add them to the cart, and prepare the sale.'}
          </p>
        </div>

        <div className="sales-cart-count">
          <ShoppingCart size={18} />
          <span>{cart.length} items</span>
        </div>
      </header>

      {checkoutStep === 'completed' && completedSale ? (
        <section className="sales-completion-panel">
          <CheckCircle size={48} />
          <h2>Payment received</h2>
          <p>Sale completed successfully.</p>

          <div className="sales-receipt-items">
            <strong>{completedSale.items.length} items</strong>

            {completedSale.items.map((item) => (
              <div key={item.id} className="sales-receipt-item">
                <span>
                  {item.product_name_snapshot}
                  {' · '}
                  {item.base_quantity} {item.base_unit_snapshot}
                </span>

                <strong>{formatCurrency(Number(item.total_amount))}</strong>
              </div>
            ))}
          </div>

          <div className="sales-receipt-number">
            <span>Receipt number</span>
            <strong>{completedSale.receipt_number}</strong>
          </div>

          <div className="sales-completion-total">
            <span>Total paid</span>
            <strong>{formatCurrency(Number(completedSale.total_amount))}</strong>
          </div>

          <button
            type="button"
            className="sales-checkout-button"
            onClick={startNewSale}
          >
            Start a new sale
          </button>
        </section>
      ) : (
        <div className="sales-workspace">
          <section className="sales-products-panel">
            <div className="sales-panel-heading">
              <div>
                <h2>Products</h2>
                <p>Find a product to add to this sale.</p>
              </div>
            </div>

            <div className="sales-search">
              <Search size={18} />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search by product name, SKU or brand..."
                disabled={checkoutLocked}
              />
            </div>

            {isLoading ? (
              <div className="sales-empty">Loading products...</div>
            ) : isError ? (
              <div className="sales-empty sales-error">
                Unable to load products. Please refresh and try again.
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="sales-empty">No matching products found.</div>
            ) : (
              <div className="sales-product-list">
                {filteredProducts.map((product) => (
                  <button
                    type="button"
                    key={product.id}
                    className={`sales-product-option ${
                      selectedProduct?.id === product.id ? 'selected' : ''
                    }`}
                    onClick={() => selectProduct(product)}
                    disabled={checkoutLocked}
                  >
                    <span className="sales-product-icon">
                      <Package size={20} />
                    </span>

                    <span className="sales-product-info">
                      <strong>{product.name}</strong>
                      <small>{product.sku} · {product.brand}</small>
                      <span>
                        Retail {formatCurrency(Number(product.retail_price))}
                      </span>
                    </span>
                  </button>
                ))}
              </div>
            )}
          </section>

          <section className="sales-selection-panel">
            <div className="sales-panel-heading">
              <div>
                <h2>Product details</h2>
                <p>Choose pricing, packaging and quantity.</p>
              </div>
            </div>

            {!selectedProduct ? (
              <div className="sales-empty sales-selection-empty">
                <Package size={32} />
                <strong>No product selected</strong>
                <span>Select a product from the product list.</span>
              </div>
            ) : (
              <div className="sales-product-details">
                <div className="sales-selected-product">
                  <strong>{selectedProduct.name}</strong>
                  <span>{selectedProduct.sku}</span>
                </div>

                <label className="sales-field">
                  <span>Pricing type</span>

              <select
                value={pricingType}
                onChange={(event) =>
                  setPricingType(event.target.value as PricingType)
                }
                disabled={checkoutLocked}
              >
                <option value="RETAIL">Retail</option>
                <option value="WHOLESALE" disabled={!canUseWholesale}>
                  Wholesale
                </option>
              </select>

              <small>
                {canUseWholesale
                  ? `Wholesale available from ${selectedProduct.wholesale_min_quantity} ${selectedProduct.base_unit}(s).`
                  : `Wholesale requires at least ${selectedProduct.wholesale_min_quantity} ${selectedProduct.base_unit}(s).`}
              </small>
                </label>

                <label className="sales-field">
                  <span>Packaging</span>
                  <select
                    value={selectedPackagingId ?? ''}

              
                    onChange={(event) => {
                      const nextPackagingId = event.target.value
                        ? Number(event.target.value)
                        : null

                      const nextPackaging = packagingOptions.find(
                        (item) => item.id === nextPackagingId,
                      )

                      const nextConversionFactor =
                        nextPackaging?.conversion_factor ?? 1

                      const nextBaseQuantity = quantity * nextConversionFactor

                      if (
                        nextBaseQuantity < selectedProduct.wholesale_min_quantity
                      ) {
                        setPricingType('RETAIL')
                      }

                      setSelectedPackagingId(nextPackagingId)
                    }}

                    disabled={packagingLoading || checkoutLocked}
                  >
                    <option value="">
                      Base unit ({selectedProduct.base_unit})
                    </option>
                    {packagingOptions.map((packaging) => (
                      <option key={packaging.id} value={packaging.id}>
                        {packaging.name} ({packaging.conversion_factor}{' '}
                        {selectedProduct.base_unit})
                      </option>
                    ))}
                  </select>
                </label>

                <label className="sales-field">
                  <span>Quantity</span>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={quantity}

                    onChange={(event) => {
                      const nextQuantity = Math.max(
                        1,
                        Number(event.target.value) || 1,
                      )

                      const nextBaseQuantity = nextQuantity * conversionFactor

                      if (
                        nextBaseQuantity < selectedProduct.wholesale_min_quantity
                      ) {
                        setPricingType('RETAIL')
                      }

                      setQuantity(nextQuantity)
                    }}

                    disabled={checkoutLocked}
                  />
                </label>

                <div className="sales-price-summary">
                  <div>
                    <span>Price per base unit</span>
                    <strong>{formatCurrency(unitPrice)}</strong>
                  </div>
                  <div>
                    <span>Price per selected package</span>
                    <strong>{formatCurrency(packagePrice)}</strong>
                  </div>
                  <div className="sales-line-total">
                    <span>Line total</span>
                    <strong>{formatCurrency(packagePrice * quantity)}</strong>
                  </div>
                </div>

                <button
                  type="button"
                  className="sales-add-button"
                  onClick={addToCart}
                  disabled={
                    checkoutLocked ||
                    !Number.isInteger(quantity) ||
                    quantity < 1
                  }
                >
                  <Plus size={18} />
                  Add to cart
                </button>
              </div>
            )}
          </section>

          <section className="sales-cart-panel">
            <div className="sales-panel-heading">
              <div>
                <h2>Current sale</h2>
                <p>{cart.length} cart lines · {cartUnits} base units</p>
              </div>
            </div>

            {cart.length === 0 ? (
              <div className="sales-empty sales-cart-empty">
                <ShoppingCart size={32} />
                <strong>Your cart is empty</strong>
                <span>Select products to start a sale.</span>
              </div>
            ) : (
              <div className="sales-cart-list">
                {cart.map((item, index) => (
                  <article
                    className="sales-cart-item"
                    key={`${item.product.id}-${index}`}
                  >
                    <div className="sales-cart-item-top">
                      <div>
                        <strong>{item.product.name}</strong>
                        <span>
                          {item.packaging?.name ?? item.product.base_unit}
                          {' · '}
                          {item.pricingType === 'RETAIL' ? 'Retail' : 'Wholesale'}
                        </span>
                      </div>
                      <button
                        type="button"
                        className="sales-remove-button"
                        onClick={() => removeCartItem(index)}
                        aria-label={`Remove ${item.product.name}`}
                        disabled={checkoutLocked}
                      >
                        <Trash2 size={17} />
                      </button>
                    </div>

                    <div className="sales-cart-item-bottom">
                      <div className="sales-quantity-control">
                        <button
                          type="button"
                          onClick={() => updateCartQuantity(index, -1)}
                          aria-label="Decrease quantity"
                          disabled={checkoutLocked}
                        >
                          <Minus size={14} />
                        </button>
                        <strong>{item.quantity}</strong>
                        <button
                          type="button"
                          onClick={() => updateCartQuantity(index, 1)}
                          aria-label="Increase quantity"
                          disabled={checkoutLocked}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                      <strong>{formatCurrency(item.total)}</strong>
                    </div>
                  </article>
                ))}
              </div>
            )}

            <div className="sales-cart-summary">
              <div>
                <span>Subtotal</span>
                <strong>{formatCurrency(cartTotal)}</strong>
              </div>
              <div className="sales-grand-total">
                <span>Total payable</span>
                <strong>{formatCurrency(
                  draftSale ? Number(draftSale.total_amount) : cartTotal,
                )}</strong>
              </div>

              {checkoutError && (
                <div className="sales-checkout-error" role="alert">
                  {checkoutError}
                </div>
              )}

              {checkoutStep === 'cart' && (
                <button
                  type="button"
                  className="sales-checkout-button"
                  disabled={cart.length === 0 || isPreparing}
                  onClick={() => void handlePrepareSale()}
                >
                  {isPreparing ? (
                    <>
                      <LoaderCircle size={17} />
                      Preparing sale...
                    </>
                  ) : draftSale ? (
                    'Retry preparing sale'
                  ) : (
                    'Proceed to payment'
                  )}
                </button>
              )}

              {checkoutStep === 'payment' && draftSale && (
                <div className="sales-payment-form">
                  <button
                    type="button"
                    className="sales-back-button"
                    onClick={() => {
                      setCheckoutStep('cart')
                      setCheckoutError('')
                    }}
                    disabled={isPaying || Boolean(paymentPlan)}
                  >
                    <ArrowLeft size={16} />
                    Back to sale
                  </button>

                  <h3>Payment details</h3>

                  <div className="sales-payment-balance">
                    <span>Outstanding balance</span>
                    <strong>{formatCurrency(outstanding)}</strong>
                  </div>

                  <label className="sales-field">
                    <span>Payment method</span>
                    <select
                      value={paymentMode}
                      onChange={(event) => {
                        setPaymentMode(event.target.value as PaymentMode)
                        setCashAmount('')
                        setMpesaAmount('')
                        setCheckoutError('')
                      }}
                      disabled={isPaying || Boolean(paymentPlan)}
                    >
                      <option value="CASH">Cash</option>
                      <option value="MPESA">M-Pesa</option>
                      <option value="SPLIT">Split payment</option>
                    </select>
                  </label>

                  {(paymentMode === 'CASH' || paymentMode === 'SPLIT') && (
                    <label className="sales-field">
                      <span>Cash amount (KSh)</span>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={cashAmount}
                        onChange={(event) => setCashAmount(event.target.value)}
                        disabled={isPaying || Boolean(paymentPlan)}
                        placeholder="0.00"
                      />
                    </label>
                  )}

                  {(paymentMode === 'MPESA' || paymentMode === 'SPLIT') && (
                    <>
                      <label className="sales-field">
                        <span>M-Pesa amount (KSh)</span>
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          value={mpesaAmount}
                          onChange={(event) => setMpesaAmount(event.target.value)}
                          disabled={isPaying || Boolean(paymentPlan)}
                          placeholder="0.00"
                        />
                      </label>

                      <label className="sales-field">
                        <span>M-Pesa transaction reference</span>
                        <input
                          type="text"
                          maxLength={100}
                          value={mpesaReference}
                          onChange={(event) => setMpesaReference(event.target.value)}
                          disabled={isPaying || Boolean(paymentPlan)}
                          placeholder="Enter M-Pesa code"
                        />
                      </label>
                    </>
                  )}

                  {paymentPlan && (
                    <p className="sales-payment-note">
                      Payment details are locked while we reconcile the recorded
                      payments. Retry will only submit amounts not already recorded.
                    </p>
                  )}

                  <button
                    type="button"
                    className="sales-checkout-button"
                    onClick={() => void handleConfirmPayment()}
                    disabled={isPaying || outstanding < 0}
                  >
                    {isPaying ? (
                      <>
                        <LoaderCircle size={17} />
                        Processing payment...
                      </>
                    ) : paymentPlan ? (
                      'Retry / complete sale'
                    ) : (
                      'Confirm payment'
                    )}
                  </button>
                </div>
              )}

              <small>
                {checkoutStep === 'payment'
                  ? 'The sale completes only after full payment and successful stock deduction.'
                  : 'Checkout records the sale and updates inventory.'}
              </small>
            </div>
          </section>
        </div>
      )}
    </main>
  )
}
