
import { useMemo, useState } from 'react'
import {
  Banknote,
  TrendingUp,
  Wallet,
  RefreshCw,
} from 'lucide-react'

import { useProductProfitability } from './api/useProductProfitability'
import type {
  ProductProfitabilityData,
  ReportPreset,
} from './report.types'

const presets: { label: string; value: ReportPreset }[] = [
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'This week', value: 'this_week' },
  { label: 'This month', value: 'this_month' },
  { label: 'This quarter', value: 'this_quarter' },
  { label: 'This year', value: 'this_year' },
  { label: 'Custom range', value: 'custom' },
]

type SortOption = 'gross_profit' | 'revenue' | 'quantity_sold'

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export default function ProductProfitabilityPage() {
  const [preset, setPreset] = useState<ReportPreset>('this_month')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('gross_profit')

  const query = {
    preset,
    ...(preset === 'custom'
      ? { start_date: startDate, end_date: endDate }
      : {}),
  }

  const today = new Date().toLocaleDateString('en-CA')

  const customRangeValid =
    preset !== 'custom' ||
    (Boolean(startDate && endDate) &&
      startDate <= endDate &&
      endDate <= today)

  const customRangeMessage =
    preset !== 'custom'
      ? ''
      : !startDate || !endDate
        ? 'Please select both a start date and an end date.'
        : startDate > endDate
          ? 'Start date cannot be later than end date.'
          : endDate > today
            ? 'End date cannot be in the future.'
            : ''

  const { data, isLoading, isError, refetch, isFetching } =
    useProductProfitability(query, customRangeValid)

  const products = useMemo(() => data?.data ?? [], [data?.data])

  const totals = useMemo(() => {
    return products.reduce(
      (result, product) => ({
        revenue: result.revenue + Number(product.revenue),
        cost: result.cost + Number(product.cost_of_goods_sold),
        profit: result.profit + Number(product.gross_profit),
      }),
      { revenue: 0, cost: 0, profit: 0 },
    )
  }, [products])

  const sortedProducts = useMemo(() => {
    return [...products].sort(
      (a, b) => Number(b[sortBy]) - Number(a[sortBy]),
    )
  }, [products, sortBy])

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">FINANCIAL REPORTS</p>
          <h1>Product Profitability</h1>
          <p className="dashboard-subtitle">
            Understand which products generate the most revenue and profit.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => void refetch()}
          disabled={isFetching || !customRangeValid}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Reporting period</h2>
            <p>Select the period you want to analyse.</p>
          </div>
        </div>

        <div className="report-filters">
          <label>
            <span>Date range</span>
            <select
              value={preset}
              onChange={(event) =>
                setPreset(event.target.value as ReportPreset)
              }
            >
              {presets.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          {preset === 'custom' && (
            <>
              <label>
                <span>Start date</span>
                <input
                  type="date"
                  value={startDate}
                  max={today}
                  onChange={(event) => setStartDate(event.target.value)}
                />
              </label>

              <label>
                <span>End date</span>
                <input
                  type="date"
                  value={endDate}
                  max={today}
                  onChange={(event) => setEndDate(event.target.value)}
                />
              </label>
            </>
          )}
        </div>

        {customRangeMessage && (
          <p className="dashboard-error">{customRangeMessage}</p>
        )}
      </section>

      {isLoading && (
        <div className="dashboard-state">
          <p>Loading product profitability report...</p>
        </div>
      )}

      {isError && (
        <div className="dashboard-state dashboard-error">
          <h2>Unable to load report</h2>
          <p>Please check your connection and try again.</p>
          <button
            onClick={() => void refetch()}
            disabled={!customRangeValid || isFetching}
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
                <h2>Overall product performance</h2>
                <p>
                  {formatDate(data.date_range.start_date)} –{' '}
                  {formatDate(data.date_range.end_date)}
                </p>
              </div>
            </div>

            <div className="stats-grid">
              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Total revenue</span>
                  <span className="stat-card-icon">
                    <Banknote size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(totals.revenue)}
                </strong>
                <span className="stat-card-description">
                  Revenue from products sold
                </span>
              </article>

              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Cost of goods sold</span>
                  <span className="stat-card-icon">
                    <Wallet size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(totals.cost)}
                </strong>
                <span className="stat-card-description">
                  Stock cost of products sold
                </span>
              </article>

              <article className={`stat-card ${
                totals.profit >= 0 ? 'stat-card-success' : 'stat-card-warning'
              }`}>
                <div className="stat-card-top">
                  <span className="stat-card-title">Total gross profit</span>
                  <span className="stat-card-icon">
                    <TrendingUp size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(totals.profit)}
                </strong>
                <span className="stat-card-description">
                  Revenue less product costs
                </span>
              </article>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Product performance</h2>
                <p>
                  {products.length} product{products.length === 1 ? '' : 's'} sold
                  during this period.
                </p>
              </div>

              <label className="report-sort">
                <span>Sort by</span>
                <select
                  value={sortBy}
                  onChange={(event) =>
                    setSortBy(event.target.value as SortOption)
                  }
                >
                  <option value="gross_profit">Gross profit</option>
                  <option value="revenue">Revenue</option>
                  <option value="quantity_sold">Quantity sold</option>
                </select>
              </label>
            </div>

            {products.length === 0 ? (
              <div className="dashboard-state">
                <h2>No product sales found</h2>
                <p>
                  There are no completed product sales for the selected period.
                </p>
              </div>
            ) : (
              <div className="report-table-wrapper">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>SKU</th>
                      <th>Quantity sold</th>
                      <th>Revenue</th>
                      <th>Cost of goods</th>
                      <th>Gross profit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedProducts.map((product: ProductProfitabilityData) => (
                      <tr key={product.product_id}>
                        <td className="report-product-name">
                          {product.product_name}
                        </td>
                        <td>{product.product_sku}</td>
                        <td>{product.quantity_sold.toLocaleString('en-KE')}</td>
                        <td>{formatCurrency(product.revenue)}</td>
                        <td>
                          {formatCurrency(product.cost_of_goods_sold)}
                        </td>
                        <td className="report-profit-value">
                          {formatCurrency(product.gross_profit)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  )
}
