import { useState } from 'react'
import {
  Banknote,
  TrendingDown,
  TrendingUp,
  Wallet,
  RefreshCw,
} from 'lucide-react'


import { useProfitLoss } from './api/useProfitLoss'
import type { ReportPreset } from './report.types'

const presets: { label: string; value: ReportPreset }[] = [
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'This week', value: 'this_week' },
  { label: 'This month', value: 'this_month' },
  { label: 'This quarter', value: 'this_quarter' },
  { label: 'This year', value: 'this_year' },
  { label: 'Custom range', value: 'custom' },
]

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

export default function ProfitLossPage() {
  const [preset, setPreset] = useState<ReportPreset>('this_month')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

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
    useProfitLoss(query, customRangeValid)

  const report = data?.data

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">FINANCIAL REPORTS</p>
          <h1>Profit & Loss</h1>
          <p className="dashboard-subtitle">
            Understand your supermarket's revenue, costs and profitability.
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
                  onChange={(event) => setStartDate(event.target.value)}
                />
              </label>

              <label>
                <span>End date</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(event) => setEndDate(event.target.value)}
                />
              </label>
            </>
          )}
        </div>
        
        {customRangeMessage && (
          <p className="dashboard-error">
            {customRangeMessage}
          </p>
        )}



      </section>

      {isLoading && (
        <div className="dashboard-state">
          <p>Loading profit and loss report...</p>
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

      {report && (
        <>
          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Financial performance</h2>
                <p>
                  {formatDate(data.date_range.start_date)} –{' '}
                  {formatDate(data.date_range.end_date)}
                </p>
              </div>
            </div>

            <div className="stats-grid">
              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Sales revenue</span>
                  <span className="stat-card-icon">
                    <Banknote size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.sales_revenue)}
                </strong>
                <span className="stat-card-description">
                  Revenue from completed sales
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
                  {formatCurrency(report.cost_of_goods_sold)}
                </strong>
                <span className="stat-card-description">
                  Cost of products sold
                </span>
              </article>

              <article className="stat-card stat-card-success">
                <div className="stat-card-top">
                  <span className="stat-card-title">Gross profit</span>
                  <span className="stat-card-icon">
                    <TrendingUp size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.gross_profit)}
                </strong>
                <span className="stat-card-description">
                  Revenue less product costs
                </span>
              </article>

              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Operating expenses</span>
                  <span className="stat-card-icon">
                    <Wallet size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.operating_expenses)}
                </strong>
                <span className="stat-card-description">
                  Recorded business expenses
                </span>
              </article>

              <article
                className={`stat-card ${
                  Number(report.net_profit) >= 0
                    ? 'stat-card-success'
                    : 'stat-card-warning'
                }`}
              >
                <div className="stat-card-top">
                  <span className="stat-card-title">Net profit</span>
                  <span className="stat-card-icon">
                    {Number(report.net_profit) >= 0 ? (
                      <TrendingUp size={20} />
                    ) : (
                      <TrendingDown size={20} />
                    )}
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.net_profit)}
                </strong>
                <span className="stat-card-description">
                  Profit after operating expenses
                </span>
              </article>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Profit calculation</h2>
                <p>How your net profit is calculated.</p>
              </div>
            </div>

            <div className="profit-breakdown">
              <div>
                <span>Sales revenue</span>
                <strong>{formatCurrency(report.sales_revenue)}</strong>
              </div>
              <div>
                <span>Less: Cost of goods sold</span>
                <strong>
                  - {formatCurrency(report.cost_of_goods_sold)}
                </strong>
              </div>
              <div className="profit-breakdown-total">
                <span>Gross profit</span>
                <strong>{formatCurrency(report.gross_profit)}</strong>
              </div>
              <div>
                <span>Less: Operating expenses</span>
                <strong>
                  - {formatCurrency(report.operating_expenses)}
                </strong>
              </div>
              <div className="profit-breakdown-net">
                <span>Net profit</span>
                <strong>{formatCurrency(report.net_profit)}</strong>
              </div>
            </div>
          </section>
        </>
      )}
    </main>
  )
}