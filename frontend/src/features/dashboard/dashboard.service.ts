
import apiClient from '../../api/client'
import type {
  CashierDashboardData,
  OwnerDashboardData,
} from './dashboard.types'

export const dashboardService = {
  async getOwnerDashboard(): Promise<OwnerDashboardData> {
    const response = await apiClient.get<OwnerDashboardData>(
      '/dashboard/owner/',
    )

    return response.data
  },

  async getCashierDashboard(): Promise<CashierDashboardData> {
    const response = await apiClient.get<CashierDashboardData>(
      '/dashboard/cashier/',
    )

    return response.data
  },
}
