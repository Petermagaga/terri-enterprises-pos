import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  getSuppliers,
  getSupplier,
  createSupplier,
  updateSupplier,
} from '../api/suppliers.service'

import type {
  CreateSupplierPayload,
  UpdateSupplierPayload,
} from '../supplier.types'

export function useSuppliers(page = 1) {
  return useQuery({
    queryKey: ['suppliers', page],
    queryFn: () => getSuppliers(page),
  })
}

export function useSupplier(id: number) {
  return useQuery({
    queryKey: ['suppliers', id],
    queryFn: () => getSupplier(id),
    enabled: id > 0,
  })
}

export function useCreateSupplier() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateSupplierPayload) =>
      createSupplier(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    },
  })
}

export function useUpdateSupplier() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: UpdateSupplierPayload
    }) => updateSupplier(id, payload),
    onSuccess: (supplier) => {
      queryClient.setQueryData(['suppliers', supplier.id], supplier)
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    },
  })
}