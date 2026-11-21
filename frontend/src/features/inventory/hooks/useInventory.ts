
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  getStockBalances,
  getPurchases,
  getPurchase,
  createPurchase,
  receivePurchase,
  getPurchaseItemsForPurchase,
  addPurchaseItem,
  getProductPackaging,
  deletePurchaseItem,
  getInventoryValuation,
  getStockAlerts,
  markAllStockAlertsRead,
} from '../api/inventory.service'

import type {
  CreatePurchasePayload,
  CreatePurchaseItemPayload,
} from '../inventory.types'
import { createProductPackaging } from '../api/inventory.service'


import type { ProductPackaging } from '../inventory.types'
import type { StockAlertsResponse } from '../inventory.types'
export function useStockBalances(page = 1) {
  return useQuery({
    queryKey: ['stock-balances', page],
    queryFn: () => getStockBalances(page),
  })
}

export function useInventoryValuation() {
  return useQuery({
    queryKey: ['inventory-valuation'],
    queryFn: getInventoryValuation,
  })
}

export function usePurchases(page = 1) {
  return useQuery({
    queryKey: ['purchases', page],
    queryFn: () => getPurchases(page),
  })
}

export function usePurchase(id: number) {
  return useQuery({
    queryKey: ['purchase', id],
    queryFn: () => getPurchase(id),
    enabled: id > 0,
  })
}

export function usePurchaseItems(purchaseId: number) {
  return useQuery({
    queryKey: ['purchase-items', purchaseId],
    queryFn: () => getPurchaseItemsForPurchase(purchaseId),
    enabled: purchaseId > 0,
  })
}

export function useProductPackaging(productId: number) {
  return useQuery({
    queryKey: ['product-packaging', productId],
    queryFn: () => getProductPackaging(productId),
    enabled: productId > 0,
  })
}

export function useCreatePurchase() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreatePurchasePayload) =>
      createPurchase(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchases'] })
    },
  })
}

export function useAddPurchaseItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreatePurchaseItemPayload) =>
      addPurchaseItem(payload),
    onSuccess: (item) => {
      queryClient.invalidateQueries({
        queryKey: ['purchase-items', item.purchase],
      })
      queryClient.invalidateQueries({
        queryKey: ['purchase', item.purchase],
      })
      queryClient.invalidateQueries({ queryKey: ['purchases'] })
    },
  })
}

export function useReceivePurchase() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (purchaseId: number) => receivePurchase(purchaseId),
    onSuccess: (purchase) => {
      queryClient.invalidateQueries({ queryKey: ['purchases'] })
      queryClient.invalidateQueries({
        queryKey: ['purchase', purchase.id],
      })
      queryClient.invalidateQueries({
        queryKey: ['purchase-items', purchase.id],
      })
      queryClient.invalidateQueries({ queryKey: ['stock-balances'] })
      queryClient.invalidateQueries({ queryKey: ['inventory-valuation'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'owner'] })
    },
  })
}



export function useCreateProductPackaging() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: Omit<ProductPackaging, 'id'>) =>
      createProductPackaging(payload),
    onSuccess: (packaging) => {
      queryClient.invalidateQueries({
        queryKey: ['product-packaging', packaging.product],
      })
    },
  })
}


export function useDeletePurchaseItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: number) => deletePurchaseItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['purchase-items'],
      })
      queryClient.invalidateQueries({
        queryKey: ['purchases'],
      })
    },

  })
}


export function useStockAlerts() {
  return useQuery({
    queryKey: ['stock-alerts'],
    queryFn: getStockAlerts,
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  })
}

export function useMarkAllStockAlertsRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: markAllStockAlertsRead,
    onSuccess: () => {
      queryClient.setQueryData<StockAlertsResponse>(
        ['stock-alerts'],
        (current) => {
          if (!current) return current

          return {
            alerts: current.alerts.map((alert) => ({
              ...alert,
              is_read: true,
            })),
            unread_count: 0,
          }
        },
      )
    },
  })
}
