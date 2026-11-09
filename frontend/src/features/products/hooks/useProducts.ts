
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { productsService } from '../api/products.service'

import type {
  CreateCategoryPayload,
  CreateProductFamilyPayload,
  CreateProductPayload,
} from '../product-catalog.types'

export function useProducts(page = 1) {
  return useQuery({
    queryKey: ['products', page],
    queryFn: () => productsService.getProducts(page),
  })
}

export function useProduct(id: number) {
  return useQuery({
    queryKey: ['products', id],
    queryFn: () => productsService.getProduct(id),
    enabled: id > 0,
  })
}

export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: productsService.getCategories,
  })
}

export function useProductFamilies() {
  return useQuery({
    queryKey: ['product-families'],
    queryFn: productsService.getProductFamilies,
  })
}

export function useCreateCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateCategoryPayload) =>
      productsService.createCategory(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })
}

export function useUpdateCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: Partial<CreateCategoryPayload>
    }) => productsService.updateCategory(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })
}

export function useCreateProductFamily() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateProductFamilyPayload) =>
      productsService.createProductFamily(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-families'] })
    },
  })
}

export function useUpdateProductFamily() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: Partial<CreateProductFamilyPayload>
    }) => productsService.updateProductFamily(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-families'] })
    },
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateProductPayload) =>
      productsService.createProduct(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export function useUpdateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: Partial<CreateProductPayload>
    }) => productsService.updateProduct(id, payload),
    onSuccess: (product) => {
      queryClient.setQueryData(['products', product.id], product)
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}
