
import { useState } from 'react'
import {
  Banknote,
  Boxes,
  CircleDollarSign,
  CreditCard,
  Package,
  ShoppingCart,
  TrendingUp,
  Wallet,
  Warehouse,
} from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { useAuth } from '../../auth/useAuth'

import { useOwnerDashboard } from './useOwnerDashboard'
import type {
  CategoryPerformance,
  TopProduct,
} from './dashboard.types'
import type { DashboardFilters, DashboardPeriod } from './dashboard.service'

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function formatCompactCurrency(value: number) {
  return new Intl.NumberFormat('en-KE', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function formatTrendDate(value: string) {
  const datePart = value.split('T')[0]
  const date = new Date(`${datePart}T00:00:00`)

  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
  })
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-KE', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function getTimeBasedGreeting() {
  const hour = new Date().getHours()

  if (hour >= 5 && hour < 12) return 'Good morning'
  if (hour >= 12 && hour < 17) return 'Good afternoon'
  if (hour >= 17 && hour < 21) return 'Good evening'

  return 'Goodnight'
}

function getPeriodLabel(period: DashboardPeriod) {
  const labels: Record<DashboardPeriod, string> = {
    today: 'Today',
    yesterday: 'Yesterday',
    this_week: 'This week',
    this_month: 'This month',
    this_quarter: 'This quarter',
    this_year: 'This year',
    custom: 'Custom range',
  }

  return labels[period]
}

interface StatCardProps {
  title: string
  value: string
  description: string
  icon: React.ReactNode
  variant?: 'default' | 'success' | 'warning'
}

function StatCard({
  title,
  value,
  description,
  icon,
  variant = 'default',
}: StatCardProps) {
  return (
    <article className={`stat-card stat-card-${variant}`}>
      <div className="stat-card-top">
        <span className="stat-card-title">{title}</span>
        <span className="stat-card-icon">{icon}</span>
      </div>

      <strong className="stat-card-value">{value}</strong>

      <span className="stat-card-description">{description}</span>
    </article>
  )
}

function TopProductsTable({ products }: { products: TopProduct[] }) {
  return (
    <div className="dashboard-table-wrapper">
      <table className="dashboard-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>SKU</th>
            <th>Quantity sold</th>
            <th>Revenue</th>
            <th>Cost</th>
            <th>Gross profit</th>
          </tr>
        </thead>

        <tbody>
          {products.map((product) => (
            <tr key={product.product_id}>
              <td>{product.product_name}</td>
              <td>{product.product_sku}</td>
              <td>{product.quantity_sold.toLocaleString('en-KE')}</td>
              <td>{formatCurrency(product.revenue)}</td>
              <td>{formatCurrency(product.cost_of_goods_sold)}</td>
              <td>{formatCurrency(product.gross_profit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function CategoryPerformanceTable({
  categories,
}: {
  categories: CategoryPerformance[]
}) {
  const rankedCategories = [...categories].sort(
    (a, b) => Number(b.gross_profit) - Number(a.gross_profit),
  )

  return (
    <div className="dashboard-table-wrapper">
      <table className="dashboard-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Quantity sold</th>
            <th>Revenue</th>
            <th>Cost</th>
            <th>Gross profit</th>
          </tr>
        </thead>

        <tbody>
          {rankedCategories.map((category) => (
            <tr key={category.category_id}>
              <td>{category.category_name}</td>
              <td>{category.quantity_sold.toLocaleString('en-KE')}</td>
              <td>{formatCurrency(category.revenue)}</td>
              <td>{formatCurrency(category.cost_of_goods_sold)}</td>
              <td>{formatCurrency(category.gross_profit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface TrendChartProps {
  title: string
  description: string
  data: {
    period: string
    revenue: number | string
    gross_profit: number | string
  }[]
  dataKey: 'revenue' | 'gross_profit'
  color: string
}

function TrendChart({
  title,
  description,
  data,
  dataKey,
  color,
}: TrendChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    [dataKey]: Number(item[dataKey]) || 0,
  }))

  return (
    <section className="dashboard-chart-card">
      <div className="dashboard-chart-heading">
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
      </div>

      {chartData.length === 0 ? (
        <div className="dashboard-empty">
          No sales data recorded for this period yet.
        </div>
      ) : (
        <div className="dashboard-chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{ top: 12, right: 18, left: 8, bottom: 4 }}
            >
              <CartesianGrid
                stroke="#E8EEE9"
                strokeDasharray="4 4"
                vertical={false}
              />

              <XAxis
                dataKey="period"
                tickFormatter={formatTrendDate}
                tick={{ fill: '#64748B', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                minTickGap={20}
              />

              <YAxis
                tickFormatter={(value) =>
                  formatCompactCurrency(Number(value))
                }
                tick={{ fill: '#64748B', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={65}
              />

              <Tooltip
                labelFormatter={(label) => formatTrendDate(String(label))}
                formatter={(value) => formatCurrency(Number(value ?? 0))}
                contentStyle={{
                  border: '1px solid #E2E8F0',
                  borderRadius: 10,
                  fontSize: 12,
                }}
              />

              <Line
                type="monotone"
                dataKey={dataKey}
                name={title}
                stroke={color}
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5, strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}

export default function OwnerDashboardPage() {
  const { user } = useAuth()

  const [period, setPeriod] = useState<DashboardPeriod>('this_week')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const filters: DashboardFilters = {
    period,
    ...(period === 'custom' && startDate && endDate
      ? { start_date: startDate, end_date: endDate }
      : {}),
  }

  const customRangeReady =
    period !== 'custom' ||
    Boolean(startDate && endDate && startDate <= endDate)

  const {
    data,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useOwnerDashboard(filters)

  const handlePeriodChange = (value: DashboardPeriod) => {
    setPeriod(value)
  }

  if (period === 'custom' && !customRangeReady) {
    return (
      <main className="owner-dashboard">
        <DashboardHeader user={user} />

        <PeriodSelector
          period={period}
          startDate={startDate}
          endDate={endDate}
          onPeriodChange={handlePeriodChange}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
        />

        <div className="dashboard-empty">
          {startDate && endDate
            ? 'The start date must be on or before the end date.'
            : 'Select both a start date and an end date to view your custom reporting period.'}
        </div>
      </main>
    )
  }

  if (isLoading) {
    return (
      <div className="dashboard-state">
        <p>Loading your dashboard...</p>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="dashboard-state dashboard-error">
        <h2>Unable to load dashboard</h2>
        <p>Please check your connection and try again.</p>
        <button onClick={() => void refetch()}>Try again</button>
      </div>
    )
  }

  const financial = data.financial_summary
  const payments = data.payment_summary
  const sales = data.sales_summary
  const stock = data.stock_summary

  const dateRangeLabel =
    data.date_range.start_date === data.date_range.end_date
      ? formatDate(data.date_range.start_date)
      : `${formatDate(data.date_range.start_date)} – ${formatDate(data.date_range.end_date)}`

  return (
    <main className="owner-dashboard">
      <DashboardHeader user={user} />

      <PeriodSelector
        period={period}
        startDate={startDate}
        endDate={endDate}
        onPeriodChange={handlePeriodChange}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
      />

      {isFetching && (
        <p className="dashboard-refreshing">Updating dashboard...</p>
      )}

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Financial performance</h2>
            <p>
              {getPeriodLabel(period)} · {dateRangeLabel}
            </p>
          </div>
        </div>

        <div className="stats-grid">
          <StatCard
            title="Sales revenue"
            value={formatCurrency(financial.sales_revenue)}
            description={`${sales.sale_count} completed sales`}
            icon={<Wallet size={20} />}
          />

          <StatCard
            title="Cost of goods sold"
            value={formatCurrency(financial.cost_of_goods_sold)}
            description="Cost of products sold"
            icon={<Boxes size={20} />}
          />

          <StatCard
            title="Gross profit"
            value={formatCurrency(financial.gross_profit)}
            description="Revenue less product costs"
            icon={<TrendingUp size={20} />}
            variant="success"
          />

          <StatCard
            title="Operating expenses"
            value={formatCurrency(financial.operating_expenses)}
            description="Business operating costs"
            icon={<CreditCard size={20} />}
          />

          <StatCard
            title="Net profit"
            value={formatCurrency(financial.net_profit)}
            description="Gross profit less operating expenses"
            icon={<CircleDollarSign size={20} />}
            variant="success"
          />

          <StatCard
            title="Setup expenses"
            value={formatCurrency(financial.setup_expenses)}
            description="Separately classified setup costs"
            icon={<Package size={20} />}
          />

          <StatCard
            title="Capital expenses"
            value={formatCurrency(financial.capital_expenses)}
            description="Separately classified capital costs"
            icon={<Warehouse size={20} />}
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Sales trends</h2>
            <p>Daily performance across the selected reporting period</p>
          </div>
        </div>

        <div className="dashboard-chart-grid">
          <TrendChart
            title="Sales revenue"
            description="Daily completed sales value"
            data={data.sales_trend}
            dataKey="revenue"
            color="#166534"
          />

          <TrendChart
            title="Gross profit"
            description="Daily revenue less cost of goods sold"
            data={data.sales_trend}
            dataKey="gross_profit"
            color="#0F766E"
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Payment collections</h2>
            <p>Recorded collections from completed sales during this period</p>
          </div>
        </div>

        <div className="stats-grid payment-grid">
          <StatCard
            title="Cash collections"
            value={formatCurrency(payments.cash.total_amount)}
            description={`${payments.cash.transaction_count} transactions`}
            icon={<Banknote size={20} />}
          />

          <StatCard
            title="M-Pesa collections"
            value={formatCurrency(payments.mpesa.total_amount)}
            description={`${payments.mpesa.transaction_count} transactions`}
            icon={<Wallet size={20} />}
          />

          <StatCard
            title="Total collections"
            value={formatCurrency(payments.total_collections)}
            description={`${payments.total_transactions} transactions`}
            icon={<CircleDollarSign size={20} />}
            variant="success"
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Stock overview</h2>
            <p>Current product availability, independent of reporting period</p>
          </div>
        </div>

        <div className="stats-grid stock-grid">
          <StatCard
            title="Total products"
            value={stock.total_products.toLocaleString('en-KE')}
            description="Products in catalogue"
            icon={<Package size={20} />}
          />

          <StatCard
            title="Low stock"
            value={stock.low_stock_products.toLocaleString('en-KE')}
            description="Products requiring attention"
            icon={<Boxes size={20} />}
            variant="warning"
          />

          <StatCard
            title="Out of stock"
            value={stock.out_of_stock_products.toLocaleString('en-KE')}
            description="Products with no available stock"
            icon={<ShoppingCart size={20} />}
            variant="warning"
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Inventory valuation</h2>
            <p>Current stock value at landed cost</p>
          </div>
        </div>

        <div className="stats-grid">
          <StatCard
            title="Inventory value (at cost)"
            value={formatCurrency(
              data.inventory_valuation.total_inventory_value,
            )}
            description={`${data.inventory_valuation.products_with_stock} products with available stock`}
            icon={<Warehouse size={20} />}
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Top-performing products</h2>
            <p>Products ranked by gross profit for the selected period</p>
          </div>
        </div>

        {data.top_products.length === 0 ? (
          <div className="dashboard-empty">
            No product sales recorded for this period yet.
          </div>
        ) : (
          <TopProductsTable products={data.top_products} />
        )}
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Category performance</h2>
            <p>Categories ranked by gross profit for the selected period</p>
          </div>
        </div>

        {data.category_performance.length === 0 ? (
          <div className="dashboard-empty">
            No category sales recorded for this period yet.
          </div>
        ) : (
          <CategoryPerformanceTable
            categories={data.category_performance}
          />
        )}
      </section>
    </main>
  )
}

function DashboardHeader({
  user,
}: {
  user: ReturnType<typeof useAuth>['user']
}) {
  return (
    <header className="dashboard-header">
      <div>
        <p className="dashboard-eyebrow">OWNER OVERVIEW</p>
        <h1>
          {getTimeBasedGreeting()},{' '}
          {user?.first_name || user?.username || 'Owner'}
        </h1>
        <p className="dashboard-subtitle">
          Here is what is happening in your shop.
        </p>
      </div>

      <div className="dashboard-date">
        <span>Today</span>
        <strong>{formatDate(new Date().toISOString().slice(0, 10))}</strong>
      </div>
    </header>
  )
}

interface PeriodSelectorProps {
  period: DashboardPeriod
  startDate: string
  endDate: string
  onPeriodChange: (value: DashboardPeriod) => void
  onStartDateChange: (value: string) => void
  onEndDateChange: (value: string) => void
}

function PeriodSelector({
  period,
  startDate,
  endDate,
  onPeriodChange,
  onStartDateChange,
  onEndDateChange,
}: PeriodSelectorProps) {
  return (
    <section className="dashboard-period-panel">
      <div className="dashboard-period-heading">
        <div>
          <h2>Reporting period</h2>
          <p>Choose the dates used for financial and sales analytics</p>
        </div>

        <span className="dashboard-period-current">
          {getPeriodLabel(period)}
        </span>
      </div>

      <div className="dashboard-period-controls">
        <label className="dashboard-period-field">
          <span>Period</span>
          <select
            value={period}
            onChange={(event) =>
              onPeriodChange(event.target.value as DashboardPeriod)
            }
          >
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="this_week">This week</option>
            <option value="this_month">This month</option>
            <option value="this_quarter">This quarter</option>
            <option value="this_year">This year</option>
            <option value="custom">Custom range</option>
          </select>
        </label>

        {period === 'custom' && (
          <>
            <label className="dashboard-period-field">
              <span>Start date</span>
              <input
                type="date"
                value={startDate}
                max={endDate || undefined}
                onChange={(event) => onStartDateChange(event.target.value)}
              />
            </label>

            <label className="dashboard-period-field">
              <span>End date</span>
              <input
                type="date"
                value={endDate}
                min={startDate || undefined}
                onChange={(event) => onEndDateChange(event.target.value)}
              />
            </label>
          </>
        )}
      </div>
    </section>
  )
}
