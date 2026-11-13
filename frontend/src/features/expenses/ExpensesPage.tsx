
import { useMemo, useState } from 'react'
import {
  Receipt,
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  Pencil,
  Trash2,
} from 'lucide-react'

import type { Expense } from './expense.types'
import { useExpenses, useDeleteExpense } from './hooks/useExpenses'
import ExpenseForm from './components/ExpenseForm'

const currency = (amount: string | number) =>
  `KSh ${Number(amount).toLocaleString('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`

const categoryLabels: Record<string, string> = {
  RENT: 'Rent',
  ELECTRICITY: 'Electricity',
  WATER: 'Water',
  SALARIES: 'Salaries',
  TRANSPORT: 'Transport',
  REPAIRS: 'Repairs',
  LICENSES: 'Licenses',
  INTERNET: 'Internet',
  OTHER: 'Other',
}

export default function ExpensesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showExpenseForm, setShowExpenseForm] = useState(false)
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null)
  const [deleteError, setDeleteError] = useState('')

  const { data, isLoading, isError, error } = useExpenses(page)
  const deleteExpense = useDeleteExpense()


  const expenses = useMemo(() => data?.results ?? [], [data?.results])
  const filteredExpenses = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return expenses

    return expenses.filter((expense) =>
      [
        expense.description,
        expense.category,
        expense.payment_method,
        expense.payment_reference,
        expense.recorded_by_username,
      ].some((value) => value?.toLowerCase().includes(term)),
    )
  }, [expenses, search])

  const pageTotal = expenses.reduce(
    (total, expense) => total + Number(expense.amount),
    0,
  )

  async function handleDelete(expense: Expense) {
    const confirmed = window.confirm(
      `Are you sure you want to delete this expense?\n\n${expense.description} — ${currency(expense.amount)}\n\nThis action cannot be undone.`,
    )

    if (!confirmed) return

    setDeleteError('')

    try {
      await deleteExpense.mutateAsync(expense.id)

      if (expenses.length === 1 && page > 1) {
        setPage((current) => current - 1)
      }
    } catch {
      setDeleteError('Unable to delete expense. Please try again.')
    }
  }

  return (
    <div className="products-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">BUSINESS MANAGEMENT</span>
          <h1>Expenses</h1>
          <p>Record and monitor your supermarket operating expenses.</p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => {
            setSelectedExpense(null)
            setShowExpenseForm(true)
          }}
        >
          <Plus size={18} />
          Record Expense
        </button>
      </div>

      <div className="products-summary">
        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Receipt size={21} />
          </div>
          <div>
            <span>Expenses on this page</span>
            <strong>{expenses.length}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon active">
            <Receipt size={21} />
          </div>
          <div>
            <span>Page total</span>
            <strong>{currency(pageTotal)}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Receipt size={21} />
          </div>
          <div>
            <span>All recorded expenses</span>
            <strong>{data?.count ?? 0}</strong>
          </div>
        </div>
      </div>

      <div className="products-table-card">
        <div className="products-table-toolbar">
          <div>
            <h2>Expense Records</h2>
            <p>Review recorded expenses and their payment details.</p>
          </div>

          <div className="products-search">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search expenses..."
              value={search}
              onChange={(event) => {
                setSearch(event.target.value)
                setPage(1)
              }}
            />
          </div>
        </div>

        {deleteError && (
          <div className="products-message error">
            {deleteError}
          </div>
        )}

        {isLoading ? (
          <div className="products-message">
            Loading expenses...
          </div>
        ) : isError ? (
          <div className="products-message error">
            {error instanceof Error
              ? error.message
              : 'Unable to load expenses. Please try again.'}
          </div>
        ) : filteredExpenses.length === 0 ? (
          <div className="products-empty">
            <Receipt size={38} />
            <h3>
              {search ? 'No matching expenses' : 'No expenses recorded yet'}
            </h3>
            <p>
              {search
                ? 'Try another description, category or payment reference.'
                : 'Record your first expense to start tracking business costs.'}
            </p>
          </div>
        ) : (
          <div className="products-table-wrapper">
            <table className="products-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Description</th>
                  <th>Amount</th>
                  <th>Payment</th>
                  <th>Reference</th>
                  <th>Recorded By</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredExpenses.map((expense) => (
                  <tr key={expense.id}>
                    <td>{expense.expense_date}</td>
                    <td>
                      {categoryLabels[expense.category] ?? expense.category}
                    </td>
                    <td>
                      <strong>{expense.description}</strong>
                    </td>
                    <td>
                      <strong>{currency(expense.amount)}</strong>
                    </td>
                    <td>{expense.payment_method}</td>
                    <td>{expense.payment_reference || '—'}</td>
                    <td>{expense.recorded_by_username}</td>
                    <td>
                      <div className="product-row-actions">
                        <button
                          type="button"
                          className="icon-button"
                          title="Edit expense"
                          aria-label={`Edit ${expense.description}`}
                          onClick={() => {
                            setSelectedExpense(expense)
                            setShowExpenseForm(true)
                          }}
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          type="button"
                          className="icon-button"
                          title="Delete expense"
                          aria-label={`Delete ${expense.description}`}
                          disabled={deleteExpense.isPending}
                          onClick={() => handleDelete(expense)}
                        >
                          <Trash2 size={16} />
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
            Showing {expenses.length === 0 ? 0 : (page - 1) * 20 + 1}
            {' '}to {Math.min(page * 20, data?.count ?? 0)}
            {' '}of {data?.count ?? 0} expenses
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

      {showExpenseForm && (
        <ExpenseForm
          expense={selectedExpense ?? undefined}
          onClose={() => {
            setShowExpenseForm(false)
            setSelectedExpense(null)
          }}
        />
      )}
    </div>
  )
}
