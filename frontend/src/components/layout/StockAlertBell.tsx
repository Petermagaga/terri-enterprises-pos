
import { useEffect, useRef, useState } from 'react'
import {
  Bell,
  CheckCheck,
  PackageX,
  AlertTriangle,
} from 'lucide-react'

import {
  useStockAlerts,
  useMarkAllStockAlertsRead,
} from '../../features/inventory/hooks/useInventory'

function formatQuantity(value: number | string) {
  const quantity = Number(value)

  return Number.isFinite(quantity)
    ? quantity.toLocaleString('en-KE', {
        maximumFractionDigits: 3,
      })
    : value
}

export default function StockAlertBell() {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const { data, isLoading, isError } = useStockAlerts()
  const markAllRead = useMarkAllStockAlertsRead()

  const alerts = data?.alerts ?? []
  const unreadCount = data?.unread_count ?? 0

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)

    return () => {
      document.removeEventListener('mousedown', handleOutsideClick)
    }
  }, [])

  return (
    <div className="stock-alert-container" ref={containerRef}>
      <button
        type="button"
        className={`stock-alert-trigger${isOpen ? ' is-open' : ''}`}
        onClick={() => setIsOpen((current) => !current)}
        aria-label={`Stock notifications, ${unreadCount} unread`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="stock-alert-badge">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="stock-alert-dropdown">
          <div className="stock-alert-heading">
            <div>
              <strong>Stock alerts</strong>
              <span>
                {alerts.length === 1
                  ? '1 active alert'
                  : `${alerts.length} active alerts`}
              </span>
            </div>

            <button
              type="button"
              className="stock-alert-mark-read"
              onClick={() => markAllRead.mutate()}
              disabled={unreadCount === 0 || markAllRead.isPending}
            >
              <CheckCheck size={14} />
              {markAllRead.isPending ? 'Saving...' : 'Mark all as read'}
            </button>
          </div>

          <div className="stock-alert-list">
            {isLoading && (
              <div className="stock-alert-empty">
                Loading stock alerts...
              </div>
            )}

            {isError && (
              <div className="stock-alert-empty stock-alert-error">
                Could not load stock alerts. Please try again.
              </div>
            )}

            {!isLoading && !isError && alerts.length === 0 && (
              <div className="stock-alert-empty">
                <CheckCheck size={24} />
                <strong>All stock levels look good</strong>
                <span>No active stock alerts.</span>
              </div>
            )}

            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`stock-alert-item${alert.is_read ? '' : ' is-unread'}`}
              >
                <div className={`stock-alert-icon${alert.is_out_of_stock ? ' is-out' : ''}`}>
                  {alert.is_out_of_stock ? (
                    <PackageX size={17} />
                  ) : (
                    <AlertTriangle size={17} />
                  )}
                </div>

                <div className="stock-alert-details">
                  <div className="stock-alert-product">
                    <strong>{alert.product_name}</strong>
                    {!alert.is_read && (
                      <span className="stock-alert-unread-dot" />
                    )}
                  </div>

                  <span className="stock-alert-sku">
                    {alert.product_sku}
                  </span>

                  <span className="stock-alert-stock">
                    {alert.is_out_of_stock
                      ? 'Out of stock'
                      : 'Low stock'}
                    {' · '}
                    {formatQuantity(alert.quantity_on_hand)} {alert.base_unit}
                    {' · Reorder at '}
                    {formatQuantity(alert.reorder_level)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
