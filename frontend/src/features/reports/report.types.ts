export type ReportPreset =
  | 'today'
  | 'yesterday'
  | 'this_week'
  | 'this_month'
  | 'this_quarter'
  | 'this_year'
  | 'custom'

export interface ReportDateRange {
  start_date: string
  end_date: string
}

export interface ProfitLossData {
  sales_revenue: string
  cost_of_goods_sold: string
  gross_profit: string
  operating_expenses: string
  net_profit: string
}

export interface ProfitLossResponse {
  date_range: ReportDateRange
  data: ProfitLossData
}

export interface ProfitLossQuery {
  preset: ReportPreset
  start_date?: string
  end_date?: string
}

export interface ProductProfitabilityData {
  product_id: number
  product_name: string
  product_sku: string
  quantity_sold: number
  revenue: string
  cost_of_goods_sold: string
  gross_profit: string
}

export interface ProductProfitabilityResponse {
  date_range: ReportDateRange
  data: ProductProfitabilityData[]
}

export interface ProductProfitabilityQuery {
  preset: ReportPreset
  start_date?: string
  end_date?: string
}