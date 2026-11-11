import { useQuery } from '@tanstack/react-query'
import { reportsService } from '../api/reports.service'
import type { ProfitLossQuery } from '../report.types'

export function useProfitLoss(
  query: ProfitLossQuery,
  enabled = true,
) {
  return useQuery({
    queryKey: ['reports', 'profit-loss', query],
    queryFn: () => reportsService.getProfitLoss(query),
    enabled,
  })
}