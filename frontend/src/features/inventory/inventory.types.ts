
export interface StockBalance {
  id: number
  product: number
  product_name: string
  product_sku: string
  base_unit: string
  quantity_on_hand: number | string
  reorder_level: number
  is_low_stock: boolean
  updated_at: string
}

export type PurchaseStatus = 'DRAFT' | 'RECEIVED'

export interface ProductPackaging {
  id: number
  product: number
  name: string
  conversion_factor: number | string
  purchase_enabled: boolean
  sales_enabled: boolean
  is_active: boolean
}

export interface Purchase {
  id: number
  supplier: number
  supplier_name: string
  supplier_reference: string
  purchase_date: string
  status: PurchaseStatus
  transport_cost: number | string
  created_by: number
  created_by_username: string
  received_at: string | null
  created_at: string
  updated_at: string
}

export interface PurchaseItem {
  id: number
  purchase: number
  purchase_reference: string
  product: number
  product_name: string
  packaging: number
  packaging_name: string
  conversion_factor_snapshot: number | string
  package_quantity: number | string
  base_quantity: number | string
  purchase_unit_cost: number | string
  line_subtotal: number | string
  allocated_transport_cost: number | string
  landed_total_cost: number | string
  landed_unit_cost: number | string
  created_at: string
  updated_at: string
}

export interface CreatePurchasePayload {
  supplier: number
  supplier_reference?: string
  purchase_date?: string
  transport_cost: string
}

export interface CreatePurchaseItemPayload {
  purchase: number
  product: number
  packaging: number
  package_quantity: string
  purchase_unit_cost: string
}