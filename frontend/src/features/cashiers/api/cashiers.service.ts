
import apiClient from '../../../api/client'
import type {
  Cashier,
  PaginatedCashiers,
  CreateCashierPayload,
  UpdateCashierPayload,
  ResetCashierPasswordPayload,
} from '../cashier.types'

export const cashiersService = {
  async getCashiers(page = 1): Promise<PaginatedCashiers> {
    const response = await apiClient.get<PaginatedCashiers>(
      '/cashiers/',
      { params: { page } },
    )

    return response.data
  },

  async getCashier(id: number): Promise<Cashier> {
    const response = await apiClient.get<Cashier>(
      `/cashiers/${id}/`,
    )

    return response.data
  },

  async createCashier(payload: CreateCashierPayload): Promise<Cashier> {
    const response = await apiClient.post<Cashier>(
      '/cashiers/',
      payload,
    )

    return response.data
  },

  async updateCashier(
    id: number,
    payload: UpdateCashierPayload,
  ): Promise<Cashier> {
    const response = await apiClient.patch<Cashier>(
      `/cashiers/${id}/`,
      payload,
    )

    return response.data
  },

  async deactivateCashier(id: number): Promise<void> {
    await apiClient.delete(`/cashiers/${id}/`)
  },

  async resetCashierPassword(
    id: number,
    payload: ResetCashierPasswordPayload,
  ): Promise<void> {
    await apiClient.post(
      `/cashiers/${id}/reset-password/`,
      payload,
    )
  },
}
