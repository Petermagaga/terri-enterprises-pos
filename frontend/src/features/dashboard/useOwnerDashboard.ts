import { useQuery } from '@tanstack/react-query'

import { dashboardService } from './dashboard.service'

export function useOwnerDashboard() {
  return useQuery({
    queryKey: ['dashboard', 'owner'],
    queryFn: dashboardService.getOwnerDashboard,
  })
}