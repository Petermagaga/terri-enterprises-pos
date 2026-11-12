
import { useState } from 'react'
import {
  Banknote,
  Smartphone,
  Wallet,
  RefreshCw,
  Receipt,
} from 'lucide-react'

import { usePaymentSummary } from './api/usePaymentSummary'
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

export default function PaymentSummaryPage() {
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
    usePaymentSummary(query, customRangeValid)

  const report = data?.data

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">FINANCIAL REPORTS</p>
          <h1>Payment Summary</h1>
          <p className="dashboard-subtitle">
            Track cash and M-Pesa collections for completed sales.
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
          <p className="dashboard-error">{customRangeMessage}</p>
        )}
      </section>

      {isLoading && (
        <div className="dashboard-state">
          <p>Loading payment summary...</p>
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
                <h2>Collection overview</h2>
                <p>
                  {formatDate(data.date_range.start_date)} –{' '}
                  {formatDate(data.date_range.end_date)}
                </p>
              </div>
            </div>

            <div className="stats-grid">
              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Cash collections</span>
                  <span className="stat-card-icon">
                    <Banknote size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.cash.total_amount)}
                </strong>
                <span className="stat-card-description">
                  {report.cash.transaction_count} cash payment(s)
                </span>
              </article>

              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">M-Pesa collections</span>
                  <span className="stat-card-icon">
                    <Smartphone size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.mpesa.total_amount)}
                </strong>
                <span className="stat-card-description">
                  {report.mpesa.transaction_count} M-Pesa payment(s)
                </span>
              </article>

              <article className="stat-card stat-card-success">
                <div className="stat-card-top">
                  <span className="stat-card-title">Total collections</span>
                  <span className="stat-card-icon">
                    <Wallet size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(report.total_collections)}
                </strong>
                <span className="stat-card-description">
                  All payment methods combined
                </span>
              </article>

              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Payment transactions</span>
                  <span className="stat-card-icon">
                    <Receipt size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {report.total_transactions}
                </strong>
                <span className="stat-card-description">
                  Total recorded payment entries
                </span>
              </article>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Payment method breakdown</h2>
                <p>Collections grouped by payment method.</p>
              </div>
            </div>

            <div className="profit-breakdown">
              <div>
                <span>Cash collections</span>
                <strong>{formatCurrency(report.cash.total_amount)}</strong>
              </div>
              <div>
                <span>Cash transactions</span>
                <strong>{report.cash.transaction_count}</strong>
              </div>
              <div>
                <span>M-Pesa collections</span>
                <strong>{formatCurrency(report.mpesa.total_amount)}</strong>
              </div>
              <div>
                <span>M-Pesa transactions</span>
                <strong>{report.mpesa.transaction_count}</strong>
              </div>
              <div className="profit-breakdown-net">
                <span>Total collections</span>
                <strong>{formatCurrency(report.total_collections)}</strong>
              </div>
            </div>
          </section>
        </>
      )}
    </main>
  )
}
