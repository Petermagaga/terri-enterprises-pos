
import { useQuery } from '@tanstack/react-query'

import {
  dashboardService,
  type DashboardFilters,
} from './dashboard.service'

export function useOwnerDashboard(filters: DashboardFilters) {
  const customRangeReady =
    filters.period !== 'custom' ||
    Boolean(filters.start_date && filters.end_date)

  return useQuery({
    queryKey: ['dashboard', 'owner', filters],
    queryFn: () => dashboardService.getOwnerDashboard(filters),
    enabled: customRangeReady,
  })
}
