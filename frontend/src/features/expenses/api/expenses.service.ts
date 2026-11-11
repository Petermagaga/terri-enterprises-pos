
import apiClient from '../../../api/client'
import type {
  Expense,
  CreateExpensePayload,
  UpdateExpensePayload,
} from '../expense.types'

export interface PaginatedExpenses {
  count: number
  next: string | null
  previous: string | null
  results: Expense[]
}

export const expensesService = {
  async getExpenses(page = 1): Promise<PaginatedExpenses> {
    const response = await apiClient.get<PaginatedExpenses>(
      '/expenses/',
      {
        params: { page },
      },
    )

    return response.data
  },

  async getExpense(id: number): Promise<Expense> {
    const response = await apiClient.get<Expense>(
      `/expenses/${id}/`,
    )

    return response.data
  },

  async createExpense(payload: CreateExpensePayload): Promise<Expense> {
    const response = await apiClient.post<Expense>(
      '/expenses/',
      payload,
    )

    return response.data
  },

  async updateExpense(
    id: number,
    payload: UpdateExpensePayload,
  ): Promise<Expense> {
    const response = await apiClient.patch<Expense>(
      `/expenses/${id}/`,
      payload,
    )

    return response.data
  },

  async deleteExpense(id: number): Promise<void> {
    await apiClient.delete(`/expenses/${id}/`)
  },
}
