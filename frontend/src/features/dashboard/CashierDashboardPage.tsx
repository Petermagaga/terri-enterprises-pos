
import {
  Banknote,
  Boxes,
  CircleDollarSign,
  Package,
  ShoppingCart,
  Wallet,
} from 'lucide-react'

import { useAuth } from '../../auth/useAuth'
import { useCashierDashboard } from './useCashierDashboard'

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
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
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

export default function CashierDashboardPage() {
  const { user } = useAuth()
  const { data, isLoading, isError, refetch, isFetching } =
    useCashierDashboard()

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

  const sales = data.sales_summary
  const payments = data.payment_summary
  const stock = data.stock_summary

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">CASHIER OVERVIEW</p>
          <h1>
            Good day, {user?.first_name || user?.username || 'Cashier'}
          </h1>
          <p className="dashboard-subtitle">
            Here is your sales activity for today.
          </p>
        </div>

        <div className="dashboard-date">
          <span>Today</span>
          <strong>{formatDate(data.date)}</strong>
        </div>
      </header>

      {isFetching && (
        <p className="dashboard-refreshing">Updating dashboard...</p>
      )}

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Today's sales</h2>
            <p>Your completed sales performance</p>
          </div>
        </div>

        <div className="stats-grid">
          <StatCard
            title="Completed sales"
            value={sales.sale_count.toLocaleString('en-KE')}
            description="Sales completed today"
            icon={<ShoppingCart size={20} />}
          />

          <StatCard
            title="Sales revenue"
            value={formatCurrency(sales.revenue)}
            description="Value of your completed sales"
            icon={<Wallet size={20} />}
            variant="success"
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Payment collections</h2>
            <p>Payments received from your completed sales today</p>
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
            <p>Current product availability</p>
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
            <h2>Recent sales</h2>
            <p>Your last seven days of completed sales</p>
          </div>
        </div>

        {data.recent_sales.length === 0 ? (
          <div className="dashboard-empty">
            You have no completed sales in the last seven days.
          </div>
        ) : (
          <div className="dashboard-table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Receipt number</th>
                  <th>Date completed</th>
                  <th>Total amount</th>
                </tr>
              </thead>

              <tbody>
                {data.recent_sales.map((sale) => (
                  <tr key={sale.id}>
                    <td>{sale.receipt_number}</td>
                    <td>{formatDateTime(sale.completed_at)}</td>
                    <td>{formatCurrency(sale.total_amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  )
}
