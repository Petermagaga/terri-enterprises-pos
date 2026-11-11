
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { expensesService } from '../api/expenses.service'
import type {
  CreateExpensePayload,
  UpdateExpensePayload,
} from '../expense.types'

export function useExpenses(page = 1) {
  return useQuery({
    queryKey: ['expenses', 'list', page],
    queryFn: () => expensesService.getExpenses(page),
  })
}

export function useExpense(id: number) {
  return useQuery({
    queryKey: ['expenses', 'detail', id],
    queryFn: () => expensesService.getExpense(id),
    enabled: id > 0,
  })
}

export function useCreateExpense() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateExpensePayload) =>
      expensesService.createExpense(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['expenses'],
      })
    },
  })
}

export function useUpdateExpense() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: UpdateExpensePayload
    }) => expensesService.updateExpense(id, payload),

    onSuccess: (expense) => {
      queryClient.invalidateQueries({
        queryKey: ['expenses'],
      })

      queryClient.setQueryData(
        ['expenses', 'detail', expense.id],
        expense,
      )
    },
  })
}

export function useDeleteExpense() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      expensesService.deleteExpense(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['expenses'],
      })
    },
  })
}
