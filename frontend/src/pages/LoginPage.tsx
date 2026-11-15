
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { LockKeyhole } from 'lucide-react'

import { useAuth } from '../auth/useAuth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const user = await login({ username, password })

      if (user.role === 'OWNER') {
        navigate('/owner', { replace: true })
      } else {
        navigate('/cashier', { replace: true })
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const responseData = err.response?.data

        setError(
          typeof responseData === 'object' &&
            responseData !== null &&
            'detail' in responseData
            ? String(responseData.detail)
            : 'Invalid username or password.',
        )
      } else {
        setError('Unable to sign in. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel">

        {/* Business Branding */}
        <div className="login-brand">
          <div className="login-logo">
            <img
              src="/terri-logo.png"
              alt="TeRRi Enterprises"
            />
          </div>

          <div className="login-brand-name">
            <h1>TeRRi Enterprises</h1>
            <p>Wholesale · Retail · More for You</p>
          </div>
        </div>

        {/* Welcome */}
        <div className="login-heading">
          <span className="login-welcome-label">
            BUSINESS MANAGEMENT SYSTEM
          </span>

          <h2>Welcome back</h2>

          <p>
            Sign in to manage your business operations.
          </p>
        </div>

        {/* Authentication Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-field">
            <label htmlFor="username">Username</label>

            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Enter your username"
              autoComplete="username"
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">Password</label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={isSubmitting}
          >
            <LockKeyhole size={18} />

            <span>
              {isSubmitting ? 'Signing in...' : 'Sign in to your account'}
            </span>
          </button>
        </form>

        {/* Security Note */}
        <div className="login-security">
          <LockKeyhole size={14} />
          <span>Secure access for authorised staff only</span>
        </div>

        {/* Subtle Developer Credit */}
        <div className="login-powered">
          <span>Powered by</span>
          <strong>GAGA<span>MATRIX</span></strong>
        </div>

      </section>
    </main>
  )
}
