
import { useState } from 'react'
import { isAxiosError } from 'axios'

import { useProducts } from '../../products/hooks/useProducts'
import {
  useAddPurchaseItem,
  useProductPackaging,
} from '../hooks/useInventory'

interface PurchaseItemFormProps {
  purchaseId: number
  onClose: () => void
  onSuccess: () => void
}

export default function PurchaseItemForm({
  purchaseId,
  onClose,
  onSuccess,
}: PurchaseItemFormProps) {
  const [product, setProduct] = useState('')
  const [packaging, setPackaging] = useState('')
  const [packageQuantity, setPackageQuantity] = useState('1')
  const [purchaseUnitCost, setPurchaseUnitCost] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const { data: productsData, isLoading: isLoadingProducts } = useProducts()
  const { data: packagingData, isLoading: isLoadingPackaging } =
    useProductPackaging(Number(product))

  const addPurchaseItemMutation = useAddPurchaseItem()

  const products = (productsData?.results ?? []).filter(
    (item) => item.is_active,
  )

  const packagingOptions = (packagingData?.results ?? []).filter(
    (item) => item.is_active && item.purchase_enabled,
  )

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    try {
      await addPurchaseItemMutation.mutateAsync({
        purchase: purchaseId,
        product: Number(product),
        packaging: Number(packaging),
        package_quantity: packageQuantity,
        purchase_unit_cost: purchaseUnitCost,
      })

      onSuccess()
    } catch (error) {
      if (isAxiosError(error)) {
        const responseData = error.response?.data

        if (typeof responseData === 'string') {
          setErrorMessage(responseData)
        } else if (responseData && typeof responseData === 'object') {
          setErrorMessage(
            Object.values(responseData)
              .flat()
              .map(String)
              .join(' '),
          )
        } else {
          setErrorMessage('Unable to add this product to the purchase.')
        }
      } else {
        setErrorMessage('Something went wrong. Please try again.')
      }
    }
  }

  return (
    <div className="modal-overlay">
      <div className="product-form-modal">
        <div className="product-form-header">
          <div>
            <span className="page-eyebrow">PURCHASE MANAGEMENT</span>
            <h2>Add Purchase Item</h2>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="product-form">
          <label>
            Product
            <select
              value={product}
              onChange={(event) => {
                setProduct(event.target.value)
                setPackaging('')
              }}
              required
              disabled={isLoadingProducts}
            >
              <option value="">Select product</option>
              {products.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({item.sku})
                </option>
              ))}
            </select>
          </label>

          <label>
            Purchase Packaging
            <select
              value={packaging}
              onChange={(event) => setPackaging(event.target.value)}
              required
              disabled={!product || isLoadingPackaging}
            >
              <option value="">
                {!product
                  ? 'Select a product first'
                  : isLoadingPackaging
                    ? 'Loading packaging...'
                    : 'Select packaging'}
              </option>

              {packagingOptions.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} (×{item.conversion_factor})
                </option>
              ))}
            </select>
          </label>

          {product && !isLoadingPackaging && packagingOptions.length === 0 && (
            <p className="form-error">
              This product has no active purchase packaging. Set it up before
              adding it to a purchase.
            </p>
          )}

          <label>
            Package Quantity
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={packageQuantity}
              onChange={(event) => setPackageQuantity(event.target.value)}
              required
            />
          </label>

          <label>
            Purchase Cost Per Package (KSh)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={purchaseUnitCost}
              onChange={(event) => setPurchaseUnitCost(event.target.value)}
              placeholder="e.g. 2400.00"
              required
            />
          </label>

          {errorMessage && (
            <div className="form-error">{errorMessage}</div>
          )}

          <div className="product-form-actions">
            <button
              type="button"
              className="button-secondary"
              onClick={onClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button-primary"
              disabled={
                addPurchaseItemMutation.isPending ||
                !product ||
                !packaging ||
                !purchaseUnitCost
              }
            >
              {addPurchaseItemMutation.isPending
                ? 'Adding...'
                : 'Add Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
