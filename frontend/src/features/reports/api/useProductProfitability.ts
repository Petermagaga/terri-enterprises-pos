
import { useQuery } from '@tanstack/react-query'
import { reportsService } from '../api/reports.service'
import type { ProductProfitabilityQuery } from '../report.types'

export function useProductProfitability(
  query: ProductProfitabilityQuery,
  enabled = true,
) {
  return useQuery({
    queryKey: ['reports', 'product-profitability', query],
    queryFn: () => reportsService.getProductProfitability(query),
    enabled,
  })
}
