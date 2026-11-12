
import apiClient from '../../../api/client'
import type {
  ProfitLossQuery,
  ProfitLossResponse,
  ProductProfitabilityQuery,
  ProductProfitabilityResponse,
  PaymentSummaryQuery,
  PaymentSummaryResponse,
  SalesSummaryQuery,
  SalesSummaryResponse,
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

  async getProductProfitability(
    query: ProductProfitabilityQuery,
  ): Promise<ProductProfitabilityResponse> {
    const response = await apiClient.get<ProductProfitabilityResponse>(
      '/reports/product-profitability/',
      {
        params: query,
      },
    )

    return response.data
  },

  async getPaymentSummary(
    query: PaymentSummaryQuery,
  ): Promise<PaymentSummaryResponse> {
    const response = await apiClient.get<PaymentSummaryResponse>(
      '/reports/payment-summary/',
      { params: query },
    )
    return response.data
  },


  async getSalesSummary(
    query: SalesSummaryQuery,
  ): Promise<SalesSummaryResponse> {
    const response = await apiClient.get<SalesSummaryResponse>(
      '/reports/sales-summary/',
      { params: query },
    )
    return response.data
  },
  
}
