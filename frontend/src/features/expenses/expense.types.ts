
export type ExpenseCategory =
  | 'RENT'
  | 'ELECTRICITY'
  | 'WATER'
  | 'SALARIES'
  | 'TRANSPORT'
  | 'REPAIRS'
  | 'LICENSES'
  | 'INTERNET'
  | 'OTHER'

export type ExpensePaymentMethod = 'CASH' | 'MPESA' | 'BANK'

export interface Expense {
  id: number
  description: string
  category: ExpenseCategory
  amount: string
  expense_date: string
  payment_method: ExpensePaymentMethod
  payment_reference: string
  recorded_by: number
  recorded_by_username: string
  created_at: string
  updated_at: string
}

export interface CreateExpensePayload {
  description: string
  category: ExpenseCategory
  amount: string
  expense_date: string
  payment_method: ExpensePaymentMethod
  payment_reference: string
}

export type UpdateExpensePayload = Partial<CreateExpensePayload>
