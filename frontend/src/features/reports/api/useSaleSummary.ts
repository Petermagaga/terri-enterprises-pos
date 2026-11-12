import { useQuery } from '@tanstack/react-query'
import { reportsService } from '../api/reports.service'
import type { SalesSummaryQuery } from '../report.types'

export function useSalesSummary(
  query: SalesSummaryQuery,
  enabled = true,
) {
  return useQuery({
    queryKey: ['reports', 'sales-summary', query],
    queryFn: () => reportsService.getSalesSummary(query),
    enabled,
  })
}