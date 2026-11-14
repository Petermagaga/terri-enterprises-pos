import {
  Banknote,
  Boxes,
  CircleDollarSign,
  CreditCard,
  Package,
  ShoppingCart,
  TrendingUp,
  Wallet,
} from 'lucide-react'

import { useAuth } from '../../auth/useAuth'

import { useOwnerDashboard } from './useOwnerDashboard'
import type { TopProduct } from './dashboard.types'

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function getTimeBasedGreeting() {
  const hour = new Date().getHours()

  if (hour >= 5 && hour < 12) {
    return 'Good morning'
  }

  if (hour >= 12 && hour < 17) {
    return 'Good afternoon'
  }

  if (hour >= 17 && hour < 21) {
    return 'Good evening'
  }

  return 'Goodnight'
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-KE', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
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



export default function OwnerDashboardPage() {
  const { user } = useAuth()
  const { data, isLoading, isError, refetch, isFetching } =
    useOwnerDashboard()

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

  return (
    <main className="owner-dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">OWNER OVERVIEW</p>
          <h1>
            {getTimeBasedGreeting()}, {user?.first_name || user?.username || 'Owner'}
          </h1>
          <p className="dashboard-subtitle">
            Here is what is happening in your Shop today.
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
            <h2>Financial performance</h2>
            <p>Today's business performance</p>
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
            description="Profit after operating expenses"
            icon={<CircleDollarSign size={20} />}
            variant="success"
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Payment collections</h2>
            <p>Money received from completed sales</p>
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
          <h2>Top-performing products</h2>
          <p>Today's products ranked by gross profit</p>
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


    </main>
  )
}