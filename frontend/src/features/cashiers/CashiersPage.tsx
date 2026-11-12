import { useMemo, useState } from 'react'
import {
  Users,
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  Pencil,
  KeyRound,
  UserCheck,
  UserX,
} from 'lucide-react'

import type { Cashier } from './cashier.types'
import {
  useCashiers,
  useDeactivateCashier,
  useUpdateCashier,
} from './hooks/useCashiers'

import CashierForm from './components/CashierForm'
import ResetPasswordForm from './components/ResetPasswordForm'

export default function CashiersPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showCashierForm, setShowCashierForm] = useState(false)
  const [selectedCashier, setSelectedCashier] = useState<Cashier | null>(null)
  const [passwordCashier, setPasswordCashier] = useState<Cashier | null>(null)
  const [actionError, setActionError] = useState('')

  const { data, isLoading, isError, error } = useCashiers(page)
  const deactivateCashier = useDeactivateCashier()
  const updateCashier = useUpdateCashier()

  const cashiers = data?.results ?? []

  const filteredCashiers = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return cashiers

    return cashiers.filter((cashier) =>
      [
        cashier.username,
        cashier.first_name,
        cashier.last_name,
        cashier.email,
      ].some((value) => value?.toLowerCase().includes(term)),
    )
  }, [cashiers, search])

  const activeCount = cashiers.filter((cashier) => cashier.is_active).length
  const inactiveCount = cashiers.length - activeCount

  async function handleStatusChange(cashier: Cashier) {
    const nextStatus = !cashier.is_active

    const confirmed = window.confirm(
      nextStatus
        ? `Reactivate the account for ${cashier.username}?`
        : `Deactivate the account for ${cashier.username}?\n\nThey will no longer be able to log in.`,
    )

    if (!confirmed) return

    setActionError('')

    try {
      if (nextStatus) {
        await updateCashier.mutateAsync({
          id: cashier.id,
          payload: { is_active: true },
        })
      } else {
        await deactivateCashier.mutateAsync(cashier.id)
      }

      if (
        !nextStatus &&
        cashiers.length === 1 &&
        page > 1
      ) {
        setPage((current) => current - 1)
      }
    } catch {
      setActionError(
        `Unable to ${nextStatus ? 'reactivate' : 'deactivate'} cashier. Please try again.`,
      )
    }
  }

  return (
    <div className="products-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">BUSINESS MANAGEMENT</span>
          <h1>Cashier Management</h1>
          <p>
            Create cashier accounts and manage their access to the POS.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => {
            setSelectedCashier(null)
            setShowCashierForm(true)
          }}
        >
          <Plus size={18} />
          Add Cashier
        </button>
      </div>

      <div className="products-summary">
        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Users size={21} />
          </div>
          <div>
            <span>Cashiers on this page</span>
            <strong>{cashiers.length}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon active">
            <UserCheck size={21} />
          </div>
          <div>
            <span>Active on this page</span>
            <strong>{activeCount}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon">
            <UserX size={21} />
          </div>
          <div>
            <span>Inactive on this page</span>
            <strong>{inactiveCount}</strong>
          </div>
        </div>
      </div>

      <div className="products-table-card">
        <div className="products-table-toolbar">
          <div>
            <h2>Cashier Accounts</h2>
            <p>Review accounts and manage cashier access.</p>
          </div>

          <div className="products-search">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search cashiers..."
              value={search}
              onChange={(event) => {
                setSearch(event.target.value)
                setPage(1)
              }}
            />
          </div>
        </div>

        {actionError && (
          <div className="products-message error">
            {actionError}
          </div>
        )}

        {isLoading ? (
          <div className="products-message">
            Loading cashier accounts...
          </div>
        ) : isError ? (
          <div className="products-message error">
            {error instanceof Error
              ? error.message
              : 'Unable to load cashier accounts. Please try again.'}
          </div>
        ) : filteredCashiers.length === 0 ? (
          <div className="products-empty">
            <Users size={38} />
            <h3>
              {search
                ? 'No matching cashiers'
                : 'No cashier accounts yet'}
            </h3>
            <p>
              {search
                ? 'Try another username, name or email address.'
                : 'Create your first cashier account to get started.'}
            </p>
          </div>
        ) : (
          <div className="products-table-wrapper">
            <table className="products-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>First Name</th>
                  <th>Last Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredCashiers.map((cashier) => (
                  <tr key={cashier.id}>
                    <td>
                      <strong>{cashier.username}</strong>
                    </td>
                    <td>{cashier.first_name || '—'}</td>
                    <td>{cashier.last_name || '—'}</td>
                    <td>{cashier.email || '—'}</td>
                    <td>
                      <span
                        className={`status-badge ${
                          cashier.is_active ? 'status-active' : 'status-inactive'
                        }`}
                      >
                        {cashier.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <div className="product-row-actions">
                        <button
                          type="button"
                          className="icon-button"
                          title="Edit cashier"
                          aria-label={`Edit ${cashier.username}`}
                          onClick={() => {
                            setSelectedCashier(cashier)
                            setShowCashierForm(true)
                          }}
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          type="button"
                          className="icon-button"
                          title="Reset password"
                          aria-label={`Reset password for ${cashier.username}`}
                          onClick={() => setPasswordCashier(cashier)}
                        >
                          <KeyRound size={16} />
                        </button>

                        <button
                          type="button"
                          className="icon-button"
                          title={
                            cashier.is_active
                              ? 'Deactivate cashier'
                              : 'Reactivate cashier'
                          }
                          aria-label={
                            cashier.is_active
                              ? `Deactivate ${cashier.username}`
                              : `Reactivate ${cashier.username}`
                          }
                          disabled={
                            deactivateCashier.isPending ||
                            updateCashier.isPending
                          }
                          onClick={() => handleStatusChange(cashier)}
                        >
                          {cashier.is_active ? (
                            <UserX size={16} />
                          ) : (
                            <UserCheck size={16} />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="products-pagination">
          <span>
            Showing {cashiers.length === 0 ? 0 : (page - 1) * 20 + 1}
            {' '}to {Math.min(page * 20, data?.count ?? 0)}
            {' '}of {data?.count ?? 0} cashiers
          </span>

          <div>
            <button
              type="button"
              disabled={!data?.previous || isLoading}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              aria-label="Previous page"
            >
              <ChevronLeft size={18} />
            </button>

            <span>Page {page}</span>

            <button
              type="button"
              disabled={!data?.next || isLoading}
              onClick={() => setPage((current) => current + 1)}
              aria-label="Next page"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>

      {showCashierForm && (
        <CashierForm
          cashier={selectedCashier ?? undefined}
          onClose={() => {
            setShowCashierForm(false)
            setSelectedCashier(null)
          }}
        />
      )}

      {passwordCashier && (
        <ResetPasswordForm
          cashierId={passwordCashier.id}
          cashierUsername={passwordCashier.username}
          onClose={() => setPasswordCashier(null)}
        />
      )}
    </div>
  )
}