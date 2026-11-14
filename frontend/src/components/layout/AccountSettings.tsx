
import { useState } from 'react'
import { isAxiosError } from 'axios'
import { X } from 'lucide-react'

import { useAuth } from '../../auth/useAuth'

interface AccountSettingsProps {
  onClose: () => void
}

export default function AccountSettings({
  onClose,
}: AccountSettingsProps) {
  const { user, updateAccountSettings } = useAuth()

  const [username, setUsername] = useState(user?.username ?? '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    const usernameChanged = username.trim() !== user?.username
    const passwordChanged = newPassword.length > 0

    if (!usernameChanged && !passwordChanged) {
      setErrorMessage('Enter a new username or password to update.')
      return
    }

    if (passwordChanged && newPassword !== confirmPassword) {
      setErrorMessage('The new passwords do not match.')
      return
    }

    const payload = {
      current_password: currentPassword,
      ...(usernameChanged ? { username: username.trim() } : {}),
      ...(passwordChanged
        ? {
            new_password: newPassword,
            confirm_new_password: confirmPassword,
          }
        : {}),
    }

    setIsSaving(true)

    try {
      await updateAccountSettings(payload)
      setSuccessMessage('Your account settings have been updated.')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
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
          setErrorMessage('Unable to update account settings. Please try again.')
        }
      } else {
        setErrorMessage('An unexpected error occurred.')
      }
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="product-modal-backdrop">
      <div
        className="product-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="account-settings-title"
      >
        <div className="product-modal-header">
          <div>
            <span className="page-eyebrow">ACCOUNT MANAGEMENT</span>
            <h2 id="account-settings-title">Account Settings</h2>
            <p>Update your username or password.</p>
          </div>

          <button
            type="button"
            className="product-modal-close"
            onClick={onClose}
            aria-label="Close settings"
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
                value={username}
                onChange={(event) => setUsername(event.target.value)}
              />
            </label>

            <label>
              Current Password *
              <input
                type="password"
                required
                autoComplete="current-password"
                value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)}
              />
            </label>

            <label>
              New Password
              <input
                type="password"
                minLength={8}
                autoComplete="new-password"
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                placeholder="Leave blank to keep current password"
              />
            </label>

            <label>
              Confirm New Password
              <input
                type="password"
                minLength={8}
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
              />
            </label>
          </div>

          {errorMessage && (
            <div className="products-message error" role="alert">
              {errorMessage}
            </div>
          )}

          {successMessage && (
            <div className="products-message" role="status">
              {successMessage}
            </div>
          )}

          <div className="product-form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={isSaving}
            >
              Close
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
