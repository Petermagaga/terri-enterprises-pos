
import apiClient from '../../../api/client'
import type { PaginatedResponse } from '../../../api/api.types'
import type { Product } from '../product.types'

import type {
  Category,
  ProductFamily,
  CreateCategoryPayload,
  CreateProductFamilyPayload,
  CreateProductPayload,
} from '../product-catalog.types'

export const productsService = {
  async getProducts(page = 1): Promise<PaginatedResponse<Product>> {
    const response = await apiClient.get<PaginatedResponse<Product>>(
      '/products/',
      { params: { page } },
    )
    return response.data
  },

  async getProduct(id: number): Promise<Product> {
    const response = await apiClient.get<Product>(`/products/${id}/`)
    return response.data
  },

  async getCategories(): Promise<PaginatedResponse<Category>> {
    const response = await apiClient.get<PaginatedResponse<Category>>(
      '/categories/',
    )
    return response.data
  },

  async getProductFamilies(): Promise<PaginatedResponse<ProductFamily>> {
    const response = await apiClient.get<PaginatedResponse<ProductFamily>>(
      '/product-families/',
    )
    return response.data
  },

  async createCategory(payload: CreateCategoryPayload): Promise<Category> {
    const response = await apiClient.post<Category>('/categories/', payload)
    return response.data
  },

  async updateCategory(
    id: number,
    payload: Partial<CreateCategoryPayload>,
  ): Promise<Category> {
    const response = await apiClient.patch<Category>(
      `/categories/${id}/`,
      payload,
    )
    return response.data
  },

  async createProductFamily(
    payload: CreateProductFamilyPayload,
  ): Promise<ProductFamily> {
    const response = await apiClient.post<ProductFamily>(
      '/product-families/',
      payload,
    )
    return response.data
  },

  async updateProductFamily(
    id: number,
    payload: Partial<CreateProductFamilyPayload>,
  ): Promise<ProductFamily> {
    const response = await apiClient.patch<ProductFamily>(
      `/product-families/${id}/`,
      payload,
    )
    return response.data
  },

  async createProduct(payload: CreateProductPayload): Promise<Product> {
    const response = await apiClient.post<Product>('/products/', payload)
    return response.data
  },

  async updateProduct(
    id: number,
    payload: Partial<CreateProductPayload>,
  ): Promise<Product> {
    const response = await apiClient.patch<Product>(
      `/products/${id}/`,
      payload,
    )
    return response.data
  },
}
