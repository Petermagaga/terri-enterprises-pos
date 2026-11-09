
import apiClient from '../api/client'

export interface AuthUser {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: 'OWNER' | 'CASHIER'
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: AuthUser
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      '/auth/login/',
      credentials,
    )

    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout/')
  },

  async getCurrentUser(): Promise<AuthUser> {
    const response = await apiClient.get<AuthUser>('/auth/me/')

    return response.data
  },
}