
import { useState } from 'react'
import {
  Boxes,
  Package,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

import { useStockBalances } from './hooks/useInventory'
import PurchaseList from './components/PurchaseList'
import PurchaseForm from './components/PurchaseForm'
import PurchaseDetails from './components/PurchaseDetails'

export default function InventoryPage() {
  const [page, setPage] = useState(1)
  const [showPurchaseForm, setShowPurchaseForm] = useState(false)
  const [selectedPurchaseId, setSelectedPurchaseId] = useState<number | null>(
    null,
  )

  const { data, isLoading, isError, error } = useStockBalances(page)

  const stockBalances = data?.results ?? []

  const lowStockCount = stockBalances.filter(
    (item) => item.is_low_stock,
  ).length

  const outOfStockCount = stockBalances.filter(
    (item) => Number(item.quantity_on_hand) <= 0,
  ).length

  return (
    <div className="products-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">STOCK MANAGEMENT</span>
          <h1>Inventory</h1>
          <p>Monitor stock levels and manage supermarket inventory.</p>
        </div>
      </div>

      <div className="products-summary">
        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Boxes size={21} />
          </div>
          <div>
            <span>Total stock records</span>
            <strong>{data?.count ?? 0}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon active">
            <AlertTriangle size={21} />
          </div>
          <div>
            <span>Low stock on this page</span>
            <strong>{lowStockCount}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Package size={21} />
          </div>
          <div>
            <span>Out of stock on this page</span>
            <strong>{outOfStockCount}</strong>
          </div>
        </div>
      </div>

      <div className="products-table-card">
        <div className="products-table-toolbar">
          <div>
            <h2>Stock Balances</h2>
            <p>Current stock quantities for registered products.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="products-message">
            Loading stock balances...
          </div>
        ) : isError ? (
          <div className="products-message error">
            {error instanceof Error
              ? error.message
              : 'Unable to load stock balances. Please try again.'}
          </div>
        ) : stockBalances.length === 0 ? (
          <div className="products-empty">
            <Boxes size={38} />
            <h3>No stock records yet</h3>
            <p>
              Stock balances will appear here when purchases are received
              or stock adjustments are recorded.
            </p>
          </div>
        ) : (
          <div className="products-table-wrapper">
            <table className="products-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Quantity on Hand</th>
                  <th>Reorder Level</th>
                  <th>Stock Status</th>
                </tr>
              </thead>

              <tbody>
                {stockBalances.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.product_name}</strong>
                    </td>

                    <td>{item.product_sku}</td>

                    <td>
                      {Number(item.quantity_on_hand).toLocaleString()}
                      {' '}
                      {item.base_unit}
                    </td>

                    <td>
                      {item.reorder_level} {item.base_unit}
                    </td>

                    <td>
                      <span
                        className={`product-status ${
                          Number(item.quantity_on_hand) <= 0
                            ? 'inactive'
                            : item.is_low_stock
                              ? 'inactive'
                              : 'active'
                        }`}
                      >
                        {Number(item.quantity_on_hand) <= 0
                          ? 'Out of Stock'
                          : item.is_low_stock
                            ? 'Low Stock'
                            : 'Healthy'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="products-pagination">
          <span>
            Showing {stockBalances.length === 0 ? 0 : (page - 1) * 20 + 1}
            {' '}to {Math.min(page * 20, data?.count ?? 0)}
            {' '}of {data?.count ?? 0} stock records
          </span>

          <div>
            <button
              type="button"
              disabled={!data?.previous || isLoading}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              aria-label="Previous page"
            >
              <ChevronLeft size={18} />
            </button>

            <span>Page {page}</span>

            <button
              type="button"
              disabled={!data?.next || isLoading}
              onClick={() => setPage((current) => current + 1)}
              aria-label="Next page"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>

      <div className="purchase-section">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">SUPPLIER OPERATIONS</span>
            <h1>Purchasing</h1>
            <p>Record supplier purchases and receive stock into inventory.</p>
          </div>
        </div>

        <PurchaseList
          onSelectPurchase={setSelectedPurchaseId}
          onCreatePurchase={() => setShowPurchaseForm(true)}
        />

        {selectedPurchaseId !== null && (
          <div className="purchase-details-section">
            <PurchaseDetails
              purchaseId={selectedPurchaseId}
              onClose={() => setSelectedPurchaseId(null)}
            />
          </div>
        )}
      </div>

      {showPurchaseForm && (
        <PurchaseForm
          onClose={() => setShowPurchaseForm(false)}
          onSuccess={(purchaseId) => {
            setShowPurchaseForm(false)
            setSelectedPurchaseId(purchaseId)
          }}
        />
      )}
    </div>
  )
}
