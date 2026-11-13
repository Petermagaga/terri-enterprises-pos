
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Boxes,
  Truck,
  Receipt,
  BarChart3,
  Users,
  History,
  TrendingUp,
  Banknote,
} from 'lucide-react'

import { useAuth } from '../../auth/useAuth'
export default function Sidebar() {
  const { user } = useAuth()
  const isOwner = user?.role === 'OWNER'

  const links = [
    {
      label: 'Dashboard',
      path: isOwner ? '/owner' : '/cashier',
      icon: LayoutDashboard,
    },
    {
      label: 'Sales',
      path: '/sales',
      icon: ShoppingCart,
    },

    {
      label: 'Sales History',
      path: '/sales-history',
      icon: History,
    },

    ...(isOwner
      ? [
          { label: 'Products', path: '/products', icon: Package },
          { label: 'Inventory', path: '/inventory', icon: Boxes },
          { label: 'Suppliers', path: '/suppliers', icon: Truck },
          { label: 'Expenses', path: '/expenses', icon: Receipt },
          { label: 'Reports', path: '/reports', icon: BarChart3 },
          { label: 'Cashiers', path: '/cashiers', icon: Users },
          {
            label: 'Product Profitability',
            path: '/product-profitability',
            icon: TrendingUp,
          },

          {
            label: 'Payment Summary',
            path: '/payment-summary',
            icon: Banknote,
          },
          {
            label: 'Sales Summary',
            path: '/sales-summary',
            icon: BarChart3,
          },

        ]
      : []),
  ]

  return (
    <nav className="sidebar-navigation">
      <span className="sidebar-label">WORKSPACE</span>

      {links.map((link) => {
        const Icon = link.icon

        return (
          <NavLink
            key={link.path}
            to={link.path}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={19} />
            <span>{link.label}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}
