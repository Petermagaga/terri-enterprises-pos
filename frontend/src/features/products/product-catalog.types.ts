
export interface Category {
  id: number
  name: string
  description: string
  is_active: boolean
}

export interface ProductFamily {
  id: number
  name: string
  sku_prefix: string | null
}

export interface CreateCategoryPayload {
  name: string
  description: string
  is_active: boolean
}

export interface CreateProductFamilyPayload {
  name: string
}

export interface CreateProductPayload {
  name: string
  product_family: number
  category: number
  brand: string
  size_value: string
  size_unit: 'G' | 'KG' | 'ML' | 'L'
  base_unit: string
  retail_price: string
  wholesale_price: string
  reorder_level: number
  is_active: boolean
}
