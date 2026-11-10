import apiClient from '../../../api/client'
import type { PaginatedResponse } from '../../../api/api.types'
import type {
  Supplier,
  CreateSupplierPayload,
  UpdateSupplierPayload,
} from '../supplier.types'

export async function getSuppliers(page = 1) {
  const response = await apiClient.get<PaginatedResponse<Supplier>>(
    `/suppliers/?page=${page}`,
  )

  return response.data
}

export async function getSupplier(id: number) {
  const response = await apiClient.get<Supplier>(`/suppliers/${id}/`)

  return response.data
}

export async function createSupplier(payload: CreateSupplierPayload) {
  const response = await apiClient.post<Supplier>('/suppliers/', payload)

  return response.data
}

export async function updateSupplier(
  id: number,
  payload: UpdateSupplierPayload,
) {
  const response = await apiClient.patch<Supplier>(
    `/suppliers/${id}/`,
    payload,
  )

  return response.data
}