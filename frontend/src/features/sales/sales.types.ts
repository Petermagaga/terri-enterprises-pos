export type SaleStatus = 'DRAFT' | 'COMPLETED' | 'VOIDED'

export type PricingType = 'RETAIL' | 'WHOLESALE'

export type PaymentMethod = 'CASH' | 'MPESA'

export interface SaleItem {
  id: number
  product: number
  product_name_snapshot: string
  product_sku_snapshot: string
  base_unit_snapshot: string
  packaging: number | null
  packaging_name_snapshot: string | null
  conversion_factor_snapshot: number | null
  base_quantity: number
  pricing_type: PricingType
  quantity: number
  selling_price_per_package: number | string
  total_amount: number | string
  total_cost?: number | string
  created_at: string
}

export interface SalePayment {
  id: number
  payment_method: PaymentMethod
  amount: number | string
  reference: string | null
  received_by: number
  created_at: string
}

export interface Sale {
  id: number
  receipt_number: string | null
  processed_by: number
  status: SaleStatus
  total_amount: number | string
  total_cost?: number | string
  gross_profit?: number | string
  items: SaleItem[]
  payments: SalePayment[]
  created_at: string
  completed_at: string | null
}


export interface AddSaleItemPayload {
  product: number
  pricing_type: PricingType
  quantity: number
  packaging?: number | null
}

export interface AddSalePaymentPayload {
  payment_method: PaymentMethod
  amount: string
  reference?: string
}