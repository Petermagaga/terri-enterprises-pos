import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { salesService } from '../api/sales.service'
import type {
  AddSaleItemPayload,
  AddSalePaymentPayload,
} from '../sales.types'

export function useSales(page = 1) {
  return useQuery({
    queryKey: ['sales', page],
    queryFn: () => salesService.getSales(page),
  })
}

export function useSale(id: number) {
  return useQuery({
    queryKey: ['sales', id],
    queryFn: () => salesService.getSale(id),
    enabled: id > 0,
  })
}

export function useCreateSale() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: salesService.createSale,
    onSuccess: (sale) => {
      queryClient.setQueryData(['sales', sale.id], sale)
      queryClient.invalidateQueries({ queryKey: ['sales'] })
    },
  })
}

export function useAddSaleItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      saleId,
      payload,
    }: {
      saleId: number
      payload: AddSaleItemPayload
    }) => salesService.addItem(saleId, payload),
    onSuccess: (sale) => {
      queryClient.setQueryData(['sales', sale.id], sale)
      queryClient.invalidateQueries({ queryKey: ['sales'] })
    },
  })
}

export function useAddSalePayment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      saleId,
      payload,
    }: {
      saleId: number
      payload: AddSalePaymentPayload
    }) => salesService.addPayment(saleId, payload),
    onSuccess: (sale) => {
      queryClient.setQueryData(['sales', sale.id], sale)
      queryClient.invalidateQueries({ queryKey: ['sales'] })
    },
  })
}

export function useCompleteSale() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: salesService.completeSale,
    onSuccess: (sale) => {
      queryClient.setQueryData(['sales', sale.id], sale)
      queryClient.invalidateQueries({ queryKey: ['sales'] })
    },
  })
}