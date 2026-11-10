
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
} from '../api/inventory.service'

import type {
  CreatePurchasePayload,
  CreatePurchaseItemPayload,
} from '../inventory.types'

export function useStockBalances(page = 1) {
  return useQuery({
    queryKey: ['stock-balances', page],
    queryFn: () => getStockBalances(page),
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
    },
  })
}
