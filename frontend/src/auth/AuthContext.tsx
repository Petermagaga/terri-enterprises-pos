
import {
  useEffect,
  useState,
  type ReactNode,
} from 'react'



import {
  authService,
  type AccountSettingsPayload,
  type AuthUser,
  type LoginCredentials,
} from './auth.service'
import { AuthContext } from './auth-context'



interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const restoreSession = async () => {
      const token = localStorage.getItem('access_token')

      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const currentUser = await authService.getCurrentUser()
        setUser(currentUser)
      } catch {
        localStorage.removeItem('access_token')
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    void restoreSession()
  }, [])

  const login = async (
    credentials: LoginCredentials,
  ): Promise<AuthUser> => {
    const response = await authService.login(credentials)
    localStorage.setItem('access_token', response.token)
    setUser(response.user)

    return response.user
  }

  const updateAccountSettings = async (
    payload: AccountSettingsPayload,
  ): Promise<AuthUser> => {
    const response = await authService.updateAccountSettings(payload)
    setUser(response.user)

    return response.user
  }


  const logout = async (): Promise<void> => {
    try {
      await authService.logout()
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        login,
        updateAccountSettings,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
