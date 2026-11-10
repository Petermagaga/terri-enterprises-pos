
import { useQuery } from '@tanstack/react-query'
import { getStockBalances } from '../api/inventory.service'

export function useStockBalances(page = 1) {
  return useQuery({
    queryKey: ['stock-balances', page],
    queryFn: () => getStockBalances(page),
  })
}
