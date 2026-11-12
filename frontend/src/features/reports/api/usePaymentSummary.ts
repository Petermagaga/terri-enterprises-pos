import { useQuery } from '@tanstack/react-query'
import { reportsService } from '../api/reports.service'
import type { PaymentSummaryQuery } from '../report.types'

export function usePaymentSummary(
  query: PaymentSummaryQuery,
  enabled = true,
) {
  return useQuery({
    queryKey: ['reports', 'payment-summary', query],
    queryFn: () => reportsService.getPaymentSummary(query),
    enabled,
  })
}