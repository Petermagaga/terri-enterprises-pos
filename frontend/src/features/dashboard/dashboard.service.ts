
import apiClient from '../../api/client'
import type {
  CashierDashboardData,
  OwnerDashboardData,
} from './dashboard.types'

export type DashboardPeriod =
  | 'today'
  | 'yesterday'
  | 'this_week'
  | 'this_month'
  | 'this_quarter'
  | 'this_year'
  | 'custom'

export interface DashboardFilters {
  period: DashboardPeriod
  start_date?: string
  end_date?: string
}

export const dashboardService = {
  async getOwnerDashboard(
    filters: DashboardFilters,
  ): Promise<OwnerDashboardData> {
    const response = await apiClient.get<OwnerDashboardData>(
      '/dashboard/owner/',
      {
        params: filters,
      },
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
