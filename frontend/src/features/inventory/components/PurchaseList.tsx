
import { useState } from 'react'
import { usePurchases } from '../hooks/useInventory'

interface PurchaseListProps {
  onSelectPurchase: (purchaseId: number) => void
  onCreatePurchase: () => void
}

function formatCurrency(value: number | string) {
  return `KSh ${Number(value).toLocaleString('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

export default function PurchaseList({
  onSelectPurchase,
  onCreatePurchase,
}: PurchaseListProps) {
  const [page, setPage] = useState(1)

  const { data, isLoading, isError, error } = usePurchases(page)

  const purchases = data?.results ?? []

  return (
    <div className="products-table-card">
      <div className="products-table-toolbar">
        <div>
          <h2>Purchase History</h2>
          <p>Manage supplier purchases and stock receiving.</p>
        </div>

        <button
          className="button-primary"
          onClick={onCreatePurchase}
        >
          + New Purchase
        </button>
      </div>

      {isLoading ? (
        <div>Loading purchases...</div>
      ) : isError ? (
        <div className="form-error">
          {error instanceof Error
            ? error.message
            : 'Unable to load purchases.'}
        </div>
      ) : purchases.length === 0 ? (
        <div className="products-empty-state">
          <h3>No purchases recorded yet</h3>
          <p>Create your first purchase to start recording incoming stock.</p>
        </div>
      ) : (
        <div className="products-table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>Purchase</th>
                <th>Supplier</th>
                <th>Reference</th>
                <th>Purchase Date</th>
                <th>Transport Cost</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {purchases.map((purchase) => (
                <tr key={purchase.id}>
                  <td>#{purchase.id}</td>
                  <td>
                    <strong>{purchase.supplier_name}</strong>
                  </td>
                  <td>{purchase.supplier_reference || '—'}</td>
                  <td>{purchase.purchase_date}</td>
                  <td>{formatCurrency(purchase.transport_cost)}</td>
                  <td>
                    <span
                      className={`status-badge ${
                        purchase.status === 'RECEIVED'
                          ? 'status-active'
                          : 'status-inactive'
                      }`}
                    >
                      {purchase.status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="button-secondary"
                      onClick={() => onSelectPurchase(purchase.id)}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="products-pagination">
        <button
          className="button-secondary"
          disabled={!data?.previous || page === 1}
          onClick={() => setPage((current) => current - 1)}
        >
          Previous
        </button>

        <span>Page {page}</span>

        <button
          className="button-secondary"
          disabled={!data?.next}
          onClick={() => setPage((current) => current + 1)}
        >
          Next
        </button>
      </div>
    </div>
  )
}
