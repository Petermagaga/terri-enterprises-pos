export interface Product {
  id: number
  name: string
  product_family: number
  sku: string
  category: number
  brand: string
  size_value: number | string
  size_unit: string
  base_unit: string
  retail_price: number | string
  wholesale_price: number | string
  wholesale_min_quantity: number
  reorder_level: number
  is_active: boolean
  created_at: string
  updated_at: string
}