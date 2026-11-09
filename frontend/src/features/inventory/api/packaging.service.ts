import apiClient from '../../../api/client'
import type { PaginatedResponse } from '../../../api/api.types'
import type { ProductPackaging } from '../packaging.types'

export const packagingService = {
  async getPackaging(page = 1): Promise<PaginatedResponse<ProductPackaging>> {
    const response = await apiClient.get<PaginatedResponse<ProductPackaging>>(
      '/inventory/packaging/',
      { params: { page } },
    )

    return response.data
  },

  async getProductPackaging(
    productId: number,
    page = 1,
  ): Promise<PaginatedResponse<ProductPackaging>> {
    const response = await apiClient.get<PaginatedResponse<ProductPackaging>>(
      '/inventory/packaging/',
      { params: { product: productId, page } },
    )

    return response.data
  },
}