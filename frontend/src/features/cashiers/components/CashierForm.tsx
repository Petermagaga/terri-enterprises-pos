import { useState } from 'react'
import { isAxiosError } from 'axios'
import { X } from 'lucide-react'

import {
  useCreateCashier,
  useUpdateCashier,
} from '../hooks/useCashiers'

import type {
  Cashier,
  CreateCashierPayload,
  UpdateCashierPayload,
} from '../cashier.types'

interface CashierFormProps {
  onClose: () => void
  cashier?: Cashier
}

export default function CashierForm({
  onClose,
  cashier,
}: CashierFormProps) {
  const [form, setForm] = useState({
    username: cashier?.username ?? '',
    first_name: cashier?.first_name ?? '',
    last_name: cashier?.last_name ?? '',
    email: cashier?.email ?? '',
    password: '',
  })

  const [errorMessage, setErrorMessage] = useState('')

  const createCashier = useCreateCashier()
  const updateCashier = useUpdateCashier()

  const isEditing = Boolean(cashier)
  const isPending = createCashier.isPending || updateCashier.isPending

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    try {
      if (cashier) {
        const payload: UpdateCashierPayload = {
          username: form.username.trim(),
          first_name: form.first_name.trim(),
          last_name: form.last_name.trim(),
          email: form.email.trim(),
        }

        await updateCashier.mutateAsync({
          id: cashier.id,
          payload,
        })
      } else {
        const payload: CreateCashierPayload = {
          username: form.username.trim(),
          first_name: form.first_name.trim(),
          last_name: form.last_name.trim(),
          email: form.email.trim(),
          password: form.password,
        }

        await createCashier.mutateAsync(payload)
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
          setErrorMessage('Unable to save cashier. Please try again.')
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
        aria-labelledby="cashier-form-title"
      >
        <div className="product-modal-header">
          <div>
            <span className="page-eyebrow">CASHIER MANAGEMENT</span>

            <h2 id="cashier-form-title">
              {isEditing ? 'Edit Cashier' : 'Create Cashier Account'}
            </h2>

            <p>
              {isEditing
                ? 'Update the cashier account details below.'
                : 'Create a login account for a new cashier.'}
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
              Username *
              <input
                required
                maxLength={150}
                value={form.username}
                onChange={(event) =>
                  updateField('username', event.target.value)
                }
                placeholder="e.g. cashier01"
              />
            </label>

            <label>
              First Name
              <input
                maxLength={150}
                value={form.first_name}
                onChange={(event) =>
                  updateField('first_name', event.target.value)
                }
                placeholder="Enter first name"
              />
            </label>

            <label>
              Last Name
              <input
                maxLength={150}
                value={form.last_name}
                onChange={(event) =>
                  updateField('last_name', event.target.value)
                }
                placeholder="Enter last name"
              />
            </label>

            <label>
              Email
              <input
                type="email"
                value={form.email}
                onChange={(event) =>
                  updateField('email', event.target.value)
                }
                placeholder="Enter email address"
              />
            </label>

            {!isEditing && (
              <label>
                Initial Password *
                <input
                  type="password"
                  required
                  minLength={8}
                  value={form.password}
                  onChange={(event) =>
                    updateField('password', event.target.value)
                  }
                  placeholder="At least 8 characters"
                />
              </label>
            )}
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
                  ? 'Update Cashier'
                  : 'Create Cashier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}