
import { useState } from 'react'
import { isAxiosError } from 'axios'
import { X } from 'lucide-react'

import {
  useCreateExpense,
  useUpdateExpense,
} from '../hooks/useExpenses'

import type {
  CreateExpensePayload,
  Expense,
  ExpenseCategory,
  ExpensePaymentMethod,
} from '../expense.types'

interface ExpenseFormProps {
  onClose: () => void
  expense?: Expense
}

const initialForm = {
  description: '',
  category: 'OTHER' as ExpenseCategory,
  amount: '',
  expense_date: new Date().toLocaleDateString('en-CA'),
  payment_method: 'CASH' as ExpensePaymentMethod,
  payment_reference: '',
}

export default function ExpenseForm({
  onClose,
  expense,
}: ExpenseFormProps) {
  const [form, setForm] = useState({
    description: expense?.description ?? initialForm.description,
    category: expense?.category ?? initialForm.category,
    amount: expense?.amount ?? initialForm.amount,
    expense_date: expense?.expense_date ?? initialForm.expense_date,
    payment_method: expense?.payment_method ?? initialForm.payment_method,
    payment_reference: expense?.payment_reference ?? '',
  })

  const [errorMessage, setErrorMessage] = useState('')

  const createExpense = useCreateExpense()
  const updateExpense = useUpdateExpense()

  const isEditing = Boolean(expense)
  const isPending = createExpense.isPending || updateExpense.isPending

  function updateField(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    const payload: CreateExpensePayload = {
      description: form.description.trim(),
      category: form.category,
      amount: form.amount,
      expense_date: form.expense_date,
      payment_method: form.payment_method,
      payment_reference:
        form.payment_method === 'CASH'
          ? ''
          : form.payment_reference.trim(),
    }

    try {
      if (expense) {
        await updateExpense.mutateAsync({
          id: expense.id,
          payload,
        })
      } else {
        await createExpense.mutateAsync(payload)
      }

      onClose()
    } catch (error) {
      if (isAxiosError(error)) {
        const detail = error.response?.data

        if (typeof detail === 'string') {
          setErrorMessage(detail)
        } else if (detail && typeof detail === 'object') {
          setErrorMessage(
            Object.entries(detail)
              .map(([field, messages]) =>
                `${field}: ${
                  Array.isArray(messages)
                    ? messages.join(', ')
                    : String(messages)
                }`,
              )
              .join(' | '),
          )
        } else {
          setErrorMessage('Unable to save expense. Please try again.')
        }
      } else {
        setErrorMessage('An unexpected error occurred.')
      }
    }
  }

  const requiresReference = form.payment_method !== 'CASH'

  return (
    <div className="product-modal-backdrop">
      <div
        className="product-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="expense-form-title"
      >
        <div className="product-modal-header">
          <div>
            <span className="page-eyebrow">EXPENSE MANAGEMENT</span>
            <h2 id="expense-form-title">
              {isEditing ? 'Edit Expense' : 'Record New Expense'}
            </h2>
            <p>
              {isEditing
                ? 'Update the expense details below.'
                : 'Enter the expense details below.'}
            </p>
          </div>

          <button
            type="button"
            className="product-modal-close"
            onClick={onClose}
            aria-label="Close form"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="product-form-grid">
            <label>
              Expense Category *
              <select
                required
                value={form.category}
                onChange={(event) =>
                  updateField('category', event.target.value)
                }
              >
                <option value="RENT">Rent</option>
                <option value="ELECTRICITY">Electricity</option>
                <option value="WATER">Water</option>
                <option value="SALARIES">Salaries and wages</option>
                <option value="TRANSPORT">Transport</option>
                <option value="REPAIRS">Repairs and maintenance</option>
                <option value="LICENSES">Licenses and permits</option>
                <option value="INTERNET">Internet and communication</option>
                <option value="OTHER">Other</option>
              </select>
            </label>

            <label>
              Amount (KES) *
              <input
                type="number"
                required
                min="0.01"
                step="0.01"
                value={form.amount}
                onChange={(event) =>
                  updateField('amount', event.target.value)
                }
                placeholder="e.g. 1500.00"
              />
            </label>

            <label>
              Expense Date *
              <input
                type="date"
                required
                value={form.expense_date}
                onChange={(event) =>
                  updateField('expense_date', event.target.value)
                }
              />
            </label>

            <label>
              Payment Method *
              <select
                required
                value={form.payment_method}
                onChange={(event) => {
                  const method = event.target.value as ExpensePaymentMethod

                  setForm((current) => ({
                    ...current,
                    payment_method: method,
                    payment_reference:
                      method === 'CASH' ? '' : current.payment_reference,
                  }))
                }}
              >
                <option value="CASH">Cash</option>
                <option value="MPESA">M-Pesa</option>
                <option value="BANK">Bank</option>
              </select>
            </label>

            {requiresReference && (
              <label>
                {form.payment_method === 'MPESA'
                  ? 'M-Pesa Transaction Reference *'
                  : 'Bank Transaction Reference *'}
                <input
                  required
                  maxLength={100}
                  value={form.payment_reference}
                  onChange={(event) =>
                    updateField('payment_reference', event.target.value)
                  }
                  placeholder="Enter transaction reference"
                />
              </label>
            )}

            <label>
              {form.category === 'OTHER'
                ? 'Specify Expense *'
                : 'Description *'}
              <input
                required
                maxLength={255}
                value={form.description}
                onChange={(event) =>
                  updateField('description', event.target.value)
                }
                placeholder={
                  form.category === 'OTHER'
                    ? 'Describe what the expense was for'
                    : 'Briefly describe this expense'
                }
              />
            </label>
          </div>

          {errorMessage && (
            <div className="product-form-error">
              {errorMessage}
            </div>
          )}

          <div className="product-form-actions">
            <button
              type="button"
              className="product-cancel-button"
              onClick={onClose}
              disabled={isPending}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={isPending}
            >
              {isPending
                ? 'Saving...'
                : isEditing
                  ? 'Update Expense'
                  : 'Save Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
