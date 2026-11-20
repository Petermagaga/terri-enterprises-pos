
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
  ExpenseType,
  CostBehaviour,
} from '../expense.types'

interface ExpenseFormProps {
  onClose: () => void
  expense?: Expense
}

type ExpenseFormState = CreateExpensePayload

const categoryOptions: Record<
  ExpenseType,
  { value: ExpenseCategory; label: string }[]
> = {
  SETUP: [
    { value: 'BUSINESS_REGISTRATION', label: 'Business Registration' },
    { value: 'LICENSES_PERMITS', label: 'Licenses & Permits' },
    { value: 'INITIAL_RENT_DEPOSIT', label: 'Initial Rent Deposit' },
    { value: 'SHOP_RENOVATION', label: 'Shop Renovation & Fittings' },
    { value: 'SHELVES_DISPLAY_SETUP', label: 'Shelves & Display Setup' },
    { value: 'REFRIGERATION_SETUP', label: 'Refrigerators & Freezers Setup' },
    { value: 'INITIAL_STOCK_ARRANGEMENT', label: 'Initial Stock Arrangement' },
    { value: 'INITIAL_MARKETING', label: 'Initial Marketing & Branding' },
    { value: 'STAFF_TRAINING', label: 'Staff Recruitment & Training' },
    { value: 'UTILITY_CONNECTIONS', label: 'Utility Connections' },
    { value: 'OTHER', label: 'Other - Specify' },
  ],
  OPERATING: [
    { value: 'RENT', label: 'Rent' },
    { value: 'ELECTRICITY', label: 'Electricity' },
    { value: 'WATER', label: 'Water' },
    { value: 'INTERNET', label: 'Internet' },
    { value: 'SALARIES_WAGES', label: 'Salaries & Wages' },
    { value: 'FUEL_TRANSPORT', label: 'Fuel & Transport' },
    { value: 'LOADING_OFFLOADING', label: 'Loading & Offloading' },
    { value: 'MAINTENANCE_REPAIRS', label: 'Repairs & Maintenance' },
    { value: 'CLEANING', label: 'Cleaning & Sanitation' },
    { value: 'SECURITY', label: 'Security' },
    { value: 'MARKETING_ADVERTISING', label: 'Marketing & Advertising' },
    { value: 'INSURANCE', label: 'Insurance' },
    { value: 'PACKAGING_MATERIALS', label: 'Packaging Materials' },
    { value: 'SHOP_SUPPLIES', label: 'Shop Supplies' },
    { value: 'TELEPHONE_AIRTIME', label: 'Telephone & Airtime' },
    { value: 'BANK_CHARGES', label: 'Bank & Transaction Charges' },
    { value: 'WASTE_COLLECTION', label: 'Waste Collection' },
    { value: 'MISCELLANEOUS', label: 'Miscellaneous Expenses' },
    { value: 'OTHER', label: 'Other - Specify' },
  ],
  CAPITAL: [
    { value: 'LAND', label: 'Land' },
    { value: 'BUILDING', label: 'Building' },
    { value: 'MOTOR_VEHICLE', label: 'Motor Vehicle' },
    { value: 'REFRIGERATORS_FREEZERS', label: 'Refrigerators & Freezers' },
    { value: 'SHELVING_DISPLAY_EQUIPMENT', label: 'Shelving & Display Equipment' },
    { value: 'CHECKOUT_COUNTERS', label: 'Checkout Counters' },
    { value: 'POS_EQUIPMENT', label: 'POS Machines & Equipment' },
    { value: 'COMPUTERS_LAPTOPS', label: 'Computers & Laptops' },
    { value: 'PRINTERS', label: 'Printers' },
    { value: 'CCTV_SECURITY', label: 'CCTV & Security Equipment' },
    { value: 'GENERATORS_BACKUP', label: 'Generators & Power Backup' },
    { value: 'WEIGHING_SCALES', label: 'Weighing Scales' },
    { value: 'MACHINERY_EQUIPMENT', label: 'Machinery & Equipment' },
    { value: 'SOFTWARE_LICENSES', label: 'Software & Licenses' },
    { value: 'OTHER', label: 'Other - Specify' },
  ],
}

const expenseTypeLabels: Record<ExpenseType, string> = {
  SETUP: 'Setup Cost',
  OPERATING: 'Operating Cost',
  CAPITAL: 'Capital Expense',
}

const initialForm: ExpenseFormState = {
  expense_type: 'OPERATING',
  category: 'MISCELLANEOUS',
  custom_category: '',
  cost_behaviour: 'VARIABLE',
  description: '',
  payee: '',
  amount: '',
  expense_date: new Date().toLocaleDateString('en-CA'),
  payment_method: 'CASH',
  payment_reference: '',
  is_recurring: false,
}

export default function ExpenseForm({
  onClose,
  expense,
}: ExpenseFormProps) {
  const [form, setForm] = useState<ExpenseFormState>({
    ...initialForm,
    ...(expense
      ? {
          expense_type: expense.expense_type,
          category: expense.category,
          custom_category: expense.custom_category ?? '',
          cost_behaviour: expense.cost_behaviour,
          description: expense.description,
          payee: expense.payee ?? '',
          amount: expense.amount,
          expense_date: expense.expense_date,
          payment_method: expense.payment_method,
          payment_reference: expense.payment_reference ?? '',
          is_recurring: expense.is_recurring,
        }
      : {}),
  })

  const [errorMessage, setErrorMessage] = useState('')

  const createExpense = useCreateExpense()
  const updateExpense = useUpdateExpense()

  const isEditing = Boolean(expense)
  const isPending = createExpense.isPending || updateExpense.isPending

  const requiresReference =
    form.payment_method === 'MPESA' ||
    form.payment_method === 'BANK_TRANSFER'

  const showReference =
    form.payment_method !== 'CASH'

  function updateField<K extends keyof ExpenseFormState>(
    field: K,
    value: ExpenseFormState[K],
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  function handleExpenseTypeChange(value: ExpenseType) {
    const firstCategory = categoryOptions[value][0].value

    setForm((current) => ({
      ...current,
      expense_type: value,
      category: firstCategory,
      custom_category: '',
    }))
  }

  function handlePaymentMethodChange(value: ExpensePaymentMethod) {
    setForm((current) => ({
      ...current,
      payment_method: value,
      payment_reference:
        value === 'CASH' ? '' : current.payment_reference,
    }))
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    const payload: CreateExpensePayload = {
      ...form,
      description: form.description.trim(),
      custom_category:
        form.category === 'OTHER'
          ? form.custom_category.trim()
          : '',
      payee: form.payee.trim(),
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
                : 'Record and classify a business expense.'}
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
              Expense Type *
              <select
                required
                value={form.expense_type}
                onChange={(event) =>
                  handleExpenseTypeChange(event.target.value as ExpenseType)
                }
              >
                {Object.entries(expenseTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Expense Category *
              <select
                required
                value={form.category}
                onChange={(event) => {
                  const category = event.target.value as ExpenseCategory

                  setForm((current) => ({
                    ...current,
                    category,
                    custom_category:
                      category === 'OTHER' ? current.custom_category : '',
                  }))
                }}
              >
                {categoryOptions[form.expense_type].map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            {form.category === 'OTHER' && (
              <label>
                Specify Category *
                <input
                  required
                  maxLength={150}
                  value={form.custom_category}
                  onChange={(event) =>
                    updateField('custom_category', event.target.value)
                  }
                  placeholder="Enter the expense category"
                />
              </label>
            )}

            <label>
              Cost Behaviour *
              <select
                required
                value={form.cost_behaviour}
                onChange={(event) =>
                  updateField(
                    'cost_behaviour',
                    event.target.value as CostBehaviour,
                  )
                }
              >
                <option value="FIXED">Fixed</option>
                <option value="VARIABLE">Variable</option>
                <option value="SEMI_VARIABLE">Semi-Variable</option>
              </select>
            </label>

            <label>
              Description *
              <input
                required
                maxLength={255}
                value={form.description}
                onChange={(event) =>
                  updateField('description', event.target.value)
                }
                placeholder="What was this expense for?"
              />
            </label>

            <label>
              Payee / Supplier
              <input
                maxLength={255}
                value={form.payee}
                onChange={(event) =>
                  updateField('payee', event.target.value)
                }
                placeholder="Name of recipient or supplier"
              />
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
                onChange={(event) =>
                  handlePaymentMethodChange(
                    event.target.value as ExpensePaymentMethod,
                  )
                }
              >
                <option value="CASH">Cash</option>
                <option value="MPESA">M-Pesa</option>
                <option value="BANK_TRANSFER">Bank Transfer</option>
                <option value="CHEQUE">Cheque</option>
                <option value="CREDIT_CARD">Credit Card</option>
              </select>
            </label>

            {showReference && (
              <label>
                Payment Reference {requiresReference ? '*' : '(Optional)'}
                <input
                  required={requiresReference}
                  maxLength={100}
                  value={form.payment_reference}
                  onChange={(event) =>
                    updateField('payment_reference', event.target.value)
                  }
                  placeholder={
                    form.payment_method === 'MPESA'
                      ? 'Enter M-Pesa transaction code'
                      : form.payment_method === 'BANK_TRANSFER'
                        ? 'Enter bank transaction reference'
                        : form.payment_method === 'CHEQUE'
                          ? 'Enter cheque number if available'
                          : 'Enter card transaction reference if available'
                  }
                />
              </label>
            )}

            <label className="expense-recurring-field">
              <span>Recurring Expense</span>
              <span className="expense-recurring-control">
                <input
                  type="checkbox"
                  checked={form.is_recurring}
                  onChange={(event) =>
                    updateField('is_recurring', event.target.checked)
                  }
                />
                <span>
                  {form.is_recurring ? 'Yes, recurring' : 'No, one-time expense'}
                </span>
              </span>
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
