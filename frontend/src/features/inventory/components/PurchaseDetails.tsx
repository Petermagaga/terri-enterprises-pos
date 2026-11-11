
import { useState } from 'react'
import { isAxiosError } from 'axios'
import {
  usePurchase,
  usePurchaseItems,
  useReceivePurchase,
  useDeletePurchaseItem,
} from '../hooks/useInventory'

import PurchaseItemForm from './PurchaseItemForm'

interface PurchaseDetailsProps {
  purchaseId: number
  onClose: () => void
}

function formatCurrency(value: number | string) {
  return `KSh ${Number(value).toLocaleString('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

export default function PurchaseDetails({
  purchaseId,
  onClose,
}: PurchaseDetailsProps) {
  const [showItemForm, setShowItemForm] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const {
    data: purchase,
    isLoading: isLoadingPurchase,
    isError: isPurchaseError,
  } = usePurchase(purchaseId)

  const {
    data: itemsData,
    isLoading: isLoadingItems,
    refetch: refetchItems,
  } = usePurchaseItems(purchaseId)

  const receivePurchaseMutation = useReceivePurchase()
  const deletePurchaseItemMutation = useDeletePurchaseItem()
  const items = itemsData?.results ?? []


  async function handleDeleteItem(
    itemId: number,
    productName: string,
  ) {
    if (
      !window.confirm(
        `Remove ${productName} from this purchase? This action cannot be undone.`,
      )
    ) {
      return
    }

    setErrorMessage('')

    try {
      await deletePurchaseItemMutation.mutateAsync(itemId)
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
          setErrorMessage('Unable to remove this purchase item.')
        }
      } else {
        setErrorMessage('Something went wrong. Please try again.')
      }
    }
  }


  async function handleReceivePurchase() {
    if (
      !window.confirm(
        'Receive this purchase? This will add the items to stock and cannot be undone.',
      )
    ) {
      return
    }

    setErrorMessage('')

    try {
      await receivePurchaseMutation.mutateAsync(purchaseId)
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
          setErrorMessage('Unable to receive this purchase.')
        }
      } else {
        setErrorMessage('Something went wrong. Please try again.')
      }
    }
  }

  if (isLoadingPurchase) {
    return <div className="products-table-card">Loading purchase...</div>
  }

  if (isPurchaseError || !purchase) {
    return (
      <div className="products-table-card">
        <p className="form-error">Unable to load this purchase.</p>
        <button className="button-secondary" onClick={onClose}>
          Back
        </button>
      </div>
    )
  }

  return (
    <div className="products-table-card purchase-details">
      <div className="products-table-toolbar">
        <div>
          <span className="page-eyebrow">PURCHASE #{purchase.id}</span>
          <h2>{purchase.supplier_name}</h2>
          <p>
            {purchase.supplier_reference || 'No supplier reference'} ·{' '}
            {purchase.purchase_date}
          </p>
        </div>

        <button className="button-secondary" onClick={onClose}>
          Back to Purchases
        </button>
      </div>

      <div className="products-summary">
        <div className="summary-card">
          <span>Status</span>
          <strong>{purchase.status}</strong>
        </div>

        <div className="summary-card">
          <span>Transport Cost</span>
          <strong>{formatCurrency(purchase.transport_cost)}</strong>
        </div>

        <div className="summary-card">
          <span>Items</span>
          <strong>{items.length}</strong>
        </div>
      </div>

      <div className="products-table-toolbar">
        <div>
          <h2>Purchase Items</h2>
          <p>Product quantities and landed purchase costs.</p>
        </div>

        {purchase.status === 'DRAFT' && (
          <button
            className="button-primary"
            onClick={() => setShowItemForm(true)}
          >
            + Add Item
          </button>
        )}
      </div>

      {isLoadingItems ? (
        <div>Loading purchase items...</div>
      ) : items.length === 0 ? (
        <div className="products-empty-state">
          <h3>No items added yet</h3>
          <p>Add products before receiving this purchase.</p>
        </div>
      ) : (
        <div className="products-table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Packaging</th>
                <th>Packages</th>
                <th>Base Quantity</th>
                <th>Unit Cost</th>
                <th>Line Subtotal</th>
                <th>Transport</th>
                <th>Landed Unit Cost</th>

                
                {purchase.status === 'DRAFT' && <th>Actions</th>}
              </tr>
            </thead>

            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <strong>{item.product_name}</strong>
                  </td>
                  <td>{item.packaging_name}</td>
                  <td>{Number(item.package_quantity).toLocaleString()}</td>
                  <td>{Number(item.base_quantity).toLocaleString()}</td>
                  <td>{formatCurrency(item.purchase_unit_cost)}</td>
                  <td>{formatCurrency(item.line_subtotal)}</td>
                  <td>{formatCurrency(item.allocated_transport_cost)}</td>
                  <td>
                    <strong>{formatCurrency(item.landed_unit_cost)}</strong>
                  </td>

                  {purchase.status === 'DRAFT' && (
                    <td>
                      <button
                        className="button-secondary"
                        onClick={() =>
                          handleDeleteItem(item.id, item.product_name)
                        }
                        disabled={deletePurchaseItemMutation.isPending}
                      >
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {errorMessage && (
        <div className="form-error">{errorMessage}</div>
      )}

      {purchase.status === 'DRAFT' && (
        <div className="purchase-receive-actions">
          <button
            className="button-primary"
            onClick={handleReceivePurchase}
            disabled={items.length === 0 || receivePurchaseMutation.isPending}
          >
            {receivePurchaseMutation.isPending
              ? 'Receiving Stock...'
              : 'Receive Purchase & Update Stock'}
          </button>
        </div>
      )}

      {purchase.status === 'RECEIVED' && (
        <div className="purchase-received-notice">
          Stock has been received and inventory balances updated.
        </div>
      )}

      {showItemForm && (
        <PurchaseItemForm
          purchaseId={purchaseId}
          onClose={() => setShowItemForm(false)}
          onSuccess={() => {
            setShowItemForm(false)
            refetchItems()
          }}
        />
      )}
    </div>
  )
}
