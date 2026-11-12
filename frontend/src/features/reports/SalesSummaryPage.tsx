
import { useMemo, useState } from 'react'
import {
  Banknote,
  Receipt,
  TrendingUp,
  Wallet,
  RefreshCw,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { useSalesSummary } from './api/useSaleSummary'

import type { ReportPreset, SalesGrouping } from './report.types'

const presets: { label: string; value: ReportPreset }[] = [
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'This week', value: 'this_week' },
  { label: 'This month', value: 'this_month' },
  { label: 'This quarter', value: 'this_quarter' },
  { label: 'This year', value: 'this_year' },
  { label: 'Custom range', value: 'custom' },
]

const groupings: { label: string; value: SalesGrouping }[] = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Yearly', value: 'yearly' },
]

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function formatPeriod(value: string) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatChartPeriod(value: string) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
  })
}

export default function SalesSummaryPage() {
  const [preset, setPreset] = useState<ReportPreset>('this_month')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [groupBy, setGroupBy] = useState<SalesGrouping>('daily')

  const query = {
    preset,
    group_by: groupBy,
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
    useSalesSummary(query, customRangeValid)

  const report = data?.data ?? []

  const totals = useMemo(() => {
    return report.reduce(
      (summary, item) => ({
        saleCount: summary.saleCount + item.sale_count,
        revenue: summary.revenue + Number(item.revenue),
        cost: summary.cost + Number(item.cost_of_goods_sold),
        grossProfit: summary.grossProfit + Number(item.gross_profit),
      }),
      {
        saleCount: 0,
        revenue: 0,
        cost: 0,
        grossProfit: 0,
      },
    )
  }, [report])

  const averageSaleValue =
    totals.saleCount > 0 ? totals.revenue / totals.saleCount : 0

  const chartData = report.map((item) => ({
    ...item,
    periodLabel: formatChartPeriod(item.period),
    revenueValue: Number(item.revenue),
    costValue: Number(item.cost_of_goods_sold),
    profitValue: Number(item.gross_profit),
  }))

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">FINANCIAL REPORTS</p>
          <h1>Sales Summary</h1>
          <p className="dashboard-subtitle">
            Analyse completed sales, revenue and gross profit over time.
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
            <p>Select the period and grouping for your report.</p>
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

          <label>
            <span>Group results by</span>
            <select
              value={groupBy}
              onChange={(event) =>
                setGroupBy(event.target.value as SalesGrouping)
              }
            >
              {groupings.map((option) => (
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
          <p>Loading sales summary...</p>
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

      {!isLoading && !isError && report.length === 0 && (
        <div className="dashboard-state">
          <h2>No completed sales found</h2>
          <p>
            There are no completed sales for the selected reporting period.
          </p>
        </div>
      )}

      {report.length > 0 && (
        <>
          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Sales performance</h2>
                <p>
                  {formatPeriod(data!.date_range.start_date)} –{' '}
                  {formatPeriod(data!.date_range.end_date)}
                </p>
              </div>
            </div>

            <div className="stats-grid">
              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Completed sales</span>
                  <span className="stat-card-icon">
                    <Receipt size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {totals.saleCount}
                </strong>
                <span className="stat-card-description">
                  Completed sale transactions
                </span>
              </article>

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
                  {formatCurrency(totals.cost)}
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
                  {formatCurrency(totals.grossProfit)}
                </strong>
                <span className="stat-card-description">
                  Revenue less product costs
                </span>
              </article>

              <article className="stat-card">
                <div className="stat-card-top">
                  <span className="stat-card-title">Average sale value</span>
                  <span className="stat-card-icon">
                    <Banknote size={20} />
                  </span>
                </div>
                <strong className="stat-card-value">
                  {formatCurrency(averageSaleValue)}
                </strong>
                <span className="stat-card-description">
                  Revenue divided by completed sales
                </span>
              </article>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Sales performance over time</h2>
                <p>
                  Revenue, product costs and gross profit grouped by{' '}
                  {groupBy}.
                </p>
              </div>
            </div>

            <div className="report-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  margin={{ top: 16, right: 16, left: 16, bottom: 8 }}
                >
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis
                    dataKey="periodLabel"
                    tick={{ fontSize: 12 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tickFormatter={(value) =>
                      new Intl.NumberFormat('en-KE', {
                        notation: 'compact',
                        maximumFractionDigits: 1,
                      }).format(Number(value))
                    }
                    tick={{ fontSize: 12 }}
                    width={65}
                  />
                  <Tooltip
                    labelFormatter={(label) => `Period: ${label}`}
                    formatter={(value) =>
                      formatCurrency(Number(value ?? 0))
                    }
                  />
                  <Legend />
                  <Bar
                    dataKey="revenueValue"
                    name="Revenue"
                    fill="#2563eb"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="costValue"
                    name="Product costs"
                    fill="#d97706"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="profitValue"
                    name="Gross profit"
                    fill="#16a34a"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>Sales breakdown</h2>
                <p>Detailed figures for each reporting period.</p>
              </div>
            </div>

            <div className="report-table-wrapper">
              <table className="report-table">
                <thead>
                  <tr>
                    <th>Period</th>
                    <th>Sales</th>
                    <th>Revenue</th>
                    <th>Product costs</th>
                    <th>Gross profit</th>
                  </tr>
                </thead>
                <tbody>
                  {report.map((item) => (
                    <tr key={item.period}>
                      <td className="report-product-name">
                        {formatPeriod(item.period)}
                      </td>
                      <td>{item.sale_count}</td>
                      <td>{formatCurrency(item.revenue)}</td>
                      <td>{formatCurrency(item.cost_of_goods_sold)}</td>
                      <td className="report-profit-value">
                        {formatCurrency(item.gross_profit)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </main>
  )
}
