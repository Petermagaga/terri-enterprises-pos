
import { createContext } from 'react'

import type { AuthUser, LoginCredentials } from './auth.service'

export interface AuthContextType {
  user: AuthUser | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<AuthUser>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined,
)
