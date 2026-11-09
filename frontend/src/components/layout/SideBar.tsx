
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
} from 'lucide-react'

import { useAuth } from '../../auth/AuthContext'

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
    ...(isOwner
      ? [
          { label: 'Products', path: '/products', icon: Package },
          { label: 'Inventory', path: '/inventory', icon: Boxes },
          { label: 'Suppliers', path: '/suppliers', icon: Truck },
          { label: 'Expenses', path: '/expenses', icon: Receipt },
          { label: 'Reports', path: '/reports', icon: BarChart3 },
          { label: 'Cashiers', path: '/cashiers', icon: Users },
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
