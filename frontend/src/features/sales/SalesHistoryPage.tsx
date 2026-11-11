
import { useState } from 'react'
import {
  ChevronLeft,
  ChevronRight,
  Eye,
  LoaderCircle,
  Receipt,
} from 'lucide-react'

import { useSales, useSale } from './hooks/useSales'
import type { Sale, SaleStatus } from './sales.types'

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value))
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-KE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function getStatusLabel(status: SaleStatus) {
  switch (status) {
    case 'COMPLETED':
      return 'Completed'
    case 'VOIDED':
      return 'Voided'
    default:
      return 'Draft'
  }
}

function SaleDetails({ sale }: { sale: Sale }) {
  return (
    <section className="sales-history-details">
      <div className="sales-history-details-header">
        <div>
          <span className="sales-history-eyebrow">TRANSACTION DETAILS</span>
          <h2>{sale.receipt_number ?? `Draft sale #${sale.id}`}</h2>
        </div>
        <span className={`sales-history-status ${sale.status.toLowerCase()}`}>
          {getStatusLabel(sale.status)}
        </span>
      </div>

      <div className="sales-history-detail-summary">
        <div>
          <span>Total amount</span>
          <strong>{formatCurrency(sale.total_amount)}</strong>
        </div>
        <div>
          <span>Processed by</span>
          <strong>User #{sale.processed_by}</strong>
        </div>
        <div>
          <span>Sale date</span>
          <strong>{formatDate(sale.completed_at ?? sale.created_at)}</strong>
        </div>
      </div>

      <div className="sales-history-section">
        <h3>Items sold</h3>

        {sale.items.length === 0 ? (
          <p className="sales-history-muted">No items recorded.</p>
        ) : (
          <div className="sales-history-table-wrapper">
            <table className="sales-history-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Quantity</th>
                  <th>Pricing</th>
                  <th>Unit price</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {sale.items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.product_name_snapshot}</strong>
                      <small>{item.product_sku_snapshot}</small>
                    </td>
                    <td>
                      {item.base_quantity} {item.base_unit_snapshot}
                    </td>
                    <td>{item.pricing_type}</td>
                    <td>
                      {formatCurrency(item.selling_price_per_package)}
                    </td>
                    <td>
                      <strong>{formatCurrency(item.total_amount)}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="sales-history-section">
        <h3>Payments received</h3>

        {sale.payments.length === 0 ? (
          <p className="sales-history-muted">No payments recorded.</p>
        ) : (
          <div className="sales-history-payments">
            {sale.payments.map((payment) => (
              <div key={payment.id} className="sales-history-payment">
                <div>
                  <strong>{payment.payment_method}</strong>
                  <small>
                    {payment.reference
                      ? `Reference: ${payment.reference}`
                      : 'No reference'}
                  </small>
                </div>
                <strong>{formatCurrency(payment.amount)}</strong>
              </div>
            ))}
          </div>
        )}
      </div>

      {sale.status === 'COMPLETED' && sale.completed_at && (
        <p className="sales-history-completed">
          Completed on {formatDate(sale.completed_at)}
        </p>
      )}
    </section>
  )
}

export default function SalesHistoryPage() {
  const [page, setPage] = useState(1)
  const [selectedSaleId, setSelectedSaleId] = useState<number | null>(null)

  const {
    data,
    isLoading,
    isError,
    error,
  } = useSales(page)

  const {
    data: selectedSale,
    isLoading: isLoadingDetails,
    isError: isDetailsError,
  } = useSale(selectedSaleId ?? 0)

  const sales = data?.results ?? []
  const totalPages = data ? Math.ceil(data.count / 20) : 0

  if (isLoading) {
    return (
      <div className="sales-history-state">
        <LoaderCircle className="spin" size={28} />
        <p>Loading sales history...</p>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="sales-history-state sales-history-error">
        <p>Unable to load sales history.</p>
        <small>
          {error instanceof Error ? error.message : 'Please try again.'}
        </small>
      </div>
    )
  }

  return (
    <div className="sales-history-page">
      <header className="sales-history-header">
        <div>
          <span className="sales-history-eyebrow">TRANSACTIONS</span>
          <h1>Sales History</h1>
          <p>Review completed sales and their payment details.</p>
        </div>

        <div className="sales-history-count">
          <Receipt size={20} />
          <div>
            <strong>{data?.count ?? 0}</strong>
            <span>Total records</span>
          </div>
        </div>
      </header>

      <div className="sales-history-layout">
        <section className="sales-history-list-panel">
          <div className="sales-history-panel-heading">
            <div>
              <h2>Transactions</h2>
              <p>Page {page}{totalPages > 0 ? ` of ${totalPages}` : ''}</p>
            </div>
          </div>

          {sales.length === 0 ? (
            <div className="sales-history-empty">
              <Receipt size={34} />
              <strong>No sales found</strong>
              <p>Sales transactions will appear here.</p>
            </div>
          ) : (
            <div className="sales-history-list">
              {sales.map((sale) => (
                <button
                  key={sale.id}
                  type="button"
                  className={`sales-history-row ${
                    selectedSaleId === sale.id ? 'selected' : ''
                  }`}
                  onClick={() => setSelectedSaleId(sale.id)}
                >
                  <div className="sales-history-row-main">
                    <div>
                      <strong>
                        {sale.receipt_number ?? `Draft #${sale.id}`}
                      </strong>
                      <small>
                        {formatDate(sale.completed_at ?? sale.created_at)}
                      </small>
                    </div>
                    <span className={`sales-history-status ${sale.status.toLowerCase()}`}>
                      {getStatusLabel(sale.status)}
                    </span>
                  </div>

                  <div className="sales-history-row-footer">
                    <span>
                      {sale.items.length} item line{sale.items.length === 1 ? '' : 's'}
                    </span>
                    <strong>{formatCurrency(sale.total_amount)}</strong>
                    <Eye size={17} />
                  </div>
                </button>
              ))}
            </div>
          )}

          <div className="sales-history-pagination">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => {
                setPage((current) => current - 1)
                setSelectedSaleId(null)
              }}
            >
              <ChevronLeft size={17} />
              Previous
            </button>

            <span>
              {page} / {Math.max(totalPages, 1)}
            </span>

            <button
              type="button"
              disabled={!data?.next}
              onClick={() => {
                setPage((current) => current + 1)
                setSelectedSaleId(null)
              }}
            >
              Next
              <ChevronRight size={17} />
            </button>
          </div>
        </section>

        <section className="sales-history-detail-panel">
          {!selectedSaleId ? (
            <div className="sales-history-empty">
              <Eye size={34} />
              <strong>Select a transaction</strong>
              <p>Choose a sale to view its items and payments.</p>
            </div>
          ) : isLoadingDetails ? (
            <div className="sales-history-state">
              <LoaderCircle className="spin" size={28} />
              <p>Loading transaction details...</p>
            </div>
          ) : isDetailsError || !selectedSale ? (
            <div className="sales-history-state sales-history-error">
              Unable to load this transaction's details.
            </div>
          ) : (
            <SaleDetails sale={selectedSale} />
          )}
        </section>
      </div>
    </div>
  )
}
