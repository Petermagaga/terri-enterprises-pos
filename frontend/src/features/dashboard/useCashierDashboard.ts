
import { useQuery } from '@tanstack/react-query'

import { dashboardService } from './dashboard.service'

export function useCashierDashboard() {
  return useQuery({
    queryKey: ['dashboard', 'cashier'],
    queryFn: dashboardService.getCashierDashboard,
  })
}
