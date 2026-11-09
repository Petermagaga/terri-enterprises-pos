import apiClient from '../../../api/client'
import type { PaginatedResponse } from '../../../api/api.types'
import type {
  AddSaleItemPayload,
  AddSalePaymentPayload,
  Sale,
} from '../sales.types'

export const salesService = {
  async getSales(page = 1): Promise<PaginatedResponse<Sale>> {
    const response = await apiClient.get<PaginatedResponse<Sale>>(
      '/sales/',
      { params: { page } },
    )

    return response.data
  },

  async getSale(id: number): Promise<Sale> {
    const response = await apiClient.get<Sale>(`/sales/${id}/`)

    return response.data
  },

  async createSale(): Promise<Sale> {
    const response = await apiClient.post<Sale>('/sales/')

    return response.data
  },

  async addItem(
    saleId: number,
    payload: AddSaleItemPayload,
  ): Promise<Sale> {
    const response = await apiClient.post<Sale>(
      `/sales/${saleId}/add-item/`,
      payload,
    )

    return response.data
  },

  async addPayment(
    saleId: number,
    payload: AddSalePaymentPayload,
  ): Promise<Sale> {
    const response = await apiClient.post<Sale>(
      `/sales/${saleId}/add-payment/`,
      payload,
    )

    return response.data
  },

  async completeSale(saleId: number): Promise<Sale> {
    const response = await apiClient.post<Sale>(
      `/sales/${saleId}/complete/`,
    )

    return response.data
  },
}