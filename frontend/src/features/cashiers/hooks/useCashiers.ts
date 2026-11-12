
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { cashiersService } from '../api/cashiers.service'
import type {
  CreateCashierPayload,
  UpdateCashierPayload,
  ResetCashierPasswordPayload,
} from '../cashier.types'

export function useCashiers(page = 1) {
  return useQuery({
    queryKey: ['cashiers', 'list', page],
    queryFn: () => cashiersService.getCashiers(page),
  })
}

export function useCreateCashier() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateCashierPayload) =>
      cashiersService.createCashier(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['cashiers'],
      })
    },
  })
}

export function useUpdateCashier() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: UpdateCashierPayload
    }) => cashiersService.updateCashier(id, payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['cashiers'],
      })
    },
  })
}

export function useDeactivateCashier() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      cashiersService.deactivateCashier(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['cashiers'],
      })
    },
  })
}

export function useResetCashierPassword() {
  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: ResetCashierPasswordPayload
    }) => cashiersService.resetCashierPassword(id, payload),
  })
}