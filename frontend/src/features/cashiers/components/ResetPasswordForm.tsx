import { useState } from 'react'
import { isAxiosError } from 'axios'
import { X } from 'lucide-react'

import { useResetCashierPassword } from '../hooks/useCashiers'

interface ResetPasswordFormProps {
  cashierId: number
  cashierUsername: string
  onClose: () => void
}

export default function ResetPasswordForm({
  cashierId,
  cashierUsername,
  onClose,
}: ResetPasswordFormProps) {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const resetPassword = useResetCashierPassword()

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    if (password !== confirmPassword) {
      setErrorMessage('The passwords do not match.')
      return
    }

    try {
      await resetPassword.mutateAsync({
        id: cashierId,
        payload: { password },
      })

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
          setErrorMessage('Unable to reset password. Please try again.')
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
        aria-labelledby="reset-password-title"
      >
        <div className="product-modal-header">
          <div>
            <span className="page-eyebrow">CASHIER MANAGEMENT</span>
            <h2 id="reset-password-title">Reset Password</h2>
            <p>
              Set a new login password for {cashierUsername}.
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
              New Password *
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="At least 8 characters"
              />
            </label>

            <label>
              Confirm New Password *
              <input
                type="password"
                required
                minLength={8}
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Enter the password again"
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
              disabled={resetPassword.isPending}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={resetPassword.isPending}
            >
              {resetPassword.isPending
                ? 'Resetting...'
                : 'Reset Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}