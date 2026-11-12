
export interface Cashier {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: 'CASHIER'
  is_active: boolean
}

export interface PaginatedCashiers {
  count: number
  next: string | null
  previous: string | null
  results: Cashier[]
}

export interface CreateCashierPayload {
  username: string
  first_name: string
  last_name: string
  email: string
  password: string
}

export interface UpdateCashierPayload {
  username?: string
  first_name?: string
  last_name?: string
  email?: string
  is_active?: boolean
}

export interface ResetCashierPasswordPayload {
  password: string
}
