import apiClient from '../../api/client'
import type { OwnerDashboardData } from './dashboard.types'

export const dashboardService = {
  async getOwnerDashboard(): Promise<OwnerDashboardData> {
    const response = await apiClient.get<OwnerDashboardData>(
      '/dashboard/owner/',
    )

    return response.data
  },
}