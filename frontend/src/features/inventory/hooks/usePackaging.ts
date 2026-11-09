import { useQuery } from '@tanstack/react-query'

import { packagingService } from '../api/packaging.service'

export function usePackaging(page = 1) {
  return useQuery({
    queryKey: ['packaging', page],
    queryFn: () => packagingService.getPackaging(page),
  })
}

export function useProductPackaging(productId: number) {
  return useQuery({
    queryKey: ['packaging', 'product', productId],
    queryFn: () => packagingService.getProductPackaging(productId),
    enabled: productId > 0,
  })
}