
import { RefreshCw, Warehouse, Package } from 'lucide-react'

import { useInventoryValuation } from './hooks/useInventory'

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function formatQuantity(value: number | string, unit: string) {
  return `${Number(value).toLocaleString('en-KE', {
    maximumFractionDigits: 3,
  })} ${unit}`
}

export default function InventoryValuationPage() {
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useInventoryValuation()

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">STOCK MANAGEMENT</p>
          <h1>Inventory Valuation</h1>
          <p className="dashboard-subtitle">
            Understand the current cost value of stock available in your shop.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => void refetch()}
          disabled={isFetching}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      {isLoading && (
        <div className="dashboard-state">
          <p>Loading inventory valuation...</p>
        </div>
      )}

      {isError && (
        <div className="dashboard-state dashboard-error">
          <h2>Unable to load inventory valuation</h2>
          <p>
            {error instanceof Error
              ? error.message
              : 'Please check your connection and try again.'}
          </p>

          <button
            onClick={() => void refetch()}
            disabled={isFetching}
          >
            Try again
          </button>
        </div>
      )}

      {data && (
        <>
          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Current stock value</h2>
                <p>
                  Calculated using remaining stock at landed purchase cost,
                  including allocated transport costs.
                </p>
              </div>
            </div>

            <div className="stats-grid">
              <article className="stat-card stat-card-success">
                <div className="stat-card-top">
                  <span className="stat-card-title">
                    Total inventory value
                  </span>
                  <span className="stat-card-icon">
                    <Warehouse size={20} />
                  </span>
                </div>

                <strong className="stat-card-value">
                  {formatCurrency(data.total_inventory_value)}
                </strong>

                <span className="stat-card-description">
                  Current stock value at landed cost
                </span>
              </article>

              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">
                    Products with stock
                  </span>
                  <span className="stat-card-icon">
                    <Package size={20} />
                  </span>
                </div>

                <strong className="stat-card-value">
                  {data.products_with_stock.toLocaleString('en-KE')}
                </strong>

                <span className="stat-card-description">
                  Products with available stock
                </span>
              </article>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Product valuation breakdown</h2>
                <p>
                  The remaining quantity, average landed unit cost and total
                  cost value of each product.
                </p>
              </div>
            </div>

            {data.products.length === 0 ? (
              <div className="dashboard-state">
                <Package size={36} />
                <h2>No stock available</h2>
                <p>
                  Inventory valuation will appear here when stock is received
                  or positive stock adjustments are recorded.
                </p>
              </div>
            ) : (
              <div className="products-table-card">
                <div className="products-table-wrapper">
                  <table className="products-table">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>SKU</th>
                        <th>Quantity on Hand</th>
                        <th>Average Unit Cost</th>
                        <th>Stock Value</th>
                        <th>Status</th>
                      </tr>
                    </thead>

                    <tbody>
                      {data.products.map((product) => (
                        <tr key={product.product_id}>
                          <td>
                            <strong>{product.product_name}</strong>
                          </td>

                          <td>{product.product_sku}</td>

                          <td>
                            {formatQuantity(
                              product.quantity_on_hand,
                              product.base_unit,
                            )}
                          </td>

                          <td>{formatCurrency(product.unit_cost)}</td>

                          <td>
                            <strong>
                              {formatCurrency(product.stock_value)}
                            </strong>
                          </td>

                          <td>
                            <span
                              className={`product-status ${
                                product.is_active ? 'active' : 'inactive'
                              }`}
                            >
                              {product.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>

          <p className="dashboard-subtitle">
            Inventory value represents the cost of stock currently remaining.
            It is not the expected selling revenue or profit.
          </p>
        </>
      )}
    </main>
  )
}
