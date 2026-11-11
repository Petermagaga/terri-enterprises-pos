
import apiClient from '../../../api/client'
import type { PaginatedResponse } from '../../../api/api.types'
import type {
  StockBalance,
  Purchase,
  PurchaseItem,
  ProductPackaging,
  CreatePurchasePayload,
  CreatePurchaseItemPayload,
} from '../inventory.types'

export async function getStockBalances(page = 1) {
  const response = await apiClient.get<PaginatedResponse<StockBalance>>(
    `/inventory/stock-balances/?page=${page}`,
  )

  return response.data
}

export async function getPurchases(page = 1) {
  const response = await apiClient.get<PaginatedResponse<Purchase>>(
    `/inventory/purchases/?page=${page}`,
  )

  return response.data
}

export async function getPurchase(id: number) {
  const response = await apiClient.get<Purchase>(
    `/inventory/purchases/${id}/`,
  )

  return response.data
}

export async function createPurchase(payload: CreatePurchasePayload) {
  const response = await apiClient.post<Purchase>(
    '/inventory/purchases/',
    payload,
  )

  return response.data
}

export async function receivePurchase(id: number) {
  const response = await apiClient.post<Purchase>(
    `/inventory/purchases/${id}/receive/`,
  )

  return response.data
}

export async function getPurchaseItems(page = 1) {
  const response = await apiClient.get<PaginatedResponse<PurchaseItem>>(
    `/inventory/purchase-items/?page=${page}`,
  )

  return response.data
}

export async function getPurchaseItemsForPurchase(purchaseId: number) {
  const response = await apiClient.get<PaginatedResponse<PurchaseItem>>(
    `/inventory/purchase-items/?purchase=${purchaseId}`,
  )

  return response.data
}

export async function addPurchaseItem(payload: CreatePurchaseItemPayload) {
  const response = await apiClient.post<PurchaseItem>(
    '/inventory/purchase-items/',
    payload,
  )

  return response.data
}


export async function deletePurchaseItem(id: number) {
  await apiClient.delete(`/inventory/purchase-items/${id}/`)
}


export async function getProductPackaging(productId: number) {
  const response = await apiClient.get<PaginatedResponse<ProductPackaging>>(
    `/inventory/packaging/?product=${productId}`,
  )

  return response.data
}



export async function createProductPackaging(
  payload: Omit<ProductPackaging, 'id'>,
) {
  const response = await apiClient.post<ProductPackaging>(
    '/inventory/packaging/',
    payload,
  )

  return response.data
}
