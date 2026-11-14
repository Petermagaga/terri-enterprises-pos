
import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { LogOut, Settings } from 'lucide-react'

import { useAuth } from '../../auth/useAuth'
import AccountSettings from './AccountSettings'
import Sidebar from './SideBar'

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showAccountSettings, setShowAccountSettings] = useState(false)

  const displayName = user?.first_name || user?.username || 'User'

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-layout">
      <aside className="app-sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">T</div>
          <div>
            <h2>Terri Enterprises</h2>
            <span>POS System</span>
          </div>
        </div>

        <div className="sidebar-user">
          <div className="user-avatar">
            {displayName.charAt(0).toUpperCase()}
          </div>
          <div>
            <strong>{displayName}</strong>
            <span>{user?.role === 'OWNER' ? 'Owner' : 'Cashier'}</span>
          </div>
        </div>

        <Sidebar />

        <div className="sidebar-footer">
          <span>Terri Enterprises POS</span>
          <small>Management System</small>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-header">
          <div>
            <span className="header-greeting">Welcome back</span>
            <strong>{displayName}</strong>
          </div>

          <span className="header-role">
            {user?.role === 'OWNER' ? 'Owner Account' : 'Cashier Account'}
          </span>

          <button
            type="button"
            className="account-settings-button"
            onClick={() => setShowAccountSettings(true)}
          >
            <Settings size={17} />
            <span>Settings</span>
          </button>

          <button
            type="button"
            className="logout-button"
            onClick={() => void handleLogout()}
          >
            <LogOut size={17} />
            <span>Sign out</span>
          </button>
        </header>

        <div className="app-content">
          <Outlet />
        </div>
      </div>

      {showAccountSettings && (
        <AccountSettings
          onClose={() => setShowAccountSettings(false)}
        />
      )}
    </div>
  )
}
