import apiClient from '../../../api/client'
import type {
  ProfitLossQuery,
  ProfitLossResponse,
} from '../report.types'

export const reportsService = {
  async getProfitLoss(
    query: ProfitLossQuery,
  ): Promise<ProfitLossResponse> {
    const response = await apiClient.get<ProfitLossResponse>(
      '/reports/profit-loss/',
      {
        params: query,
      },
    )

    return response.data
  },
}