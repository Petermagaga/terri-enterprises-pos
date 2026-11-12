export interface FinancialSummary {
  start_date: string
  end_date: string
  sales_revenue: number | string
  cost_of_goods_sold: number | string
  gross_profit: number | string
  operating_expenses: number | string
  net_profit: number | string
}

export interface PaymentMethodSummary {
  total_amount: number | string
  transaction_count: number
}

export interface PaymentSummary {
  cash: PaymentMethodSummary
  mpesa: PaymentMethodSummary
  total_collections: number | string
  total_transactions: number
}

export interface SalesSummary {
  sale_count: number
  revenue: number | string
  cost_of_goods_sold: number | string
  gross_profit: number | string
}

export interface StockSummary {
  total_products: number
  low_stock_products: number
  out_of_stock_products: number
}

export interface TopProduct {
  product_id: number
  product_name: string
  product_sku: string
  quantity_sold: number
  revenue: number | string
  cost_of_goods_sold: number | string
  gross_profit: number | string
}


export interface OwnerDashboardData {
  date: string
  financial_summary: FinancialSummary
  payment_summary: PaymentSummary
  sales_summary: SalesSummary
  stock_summary: StockSummary
  top_products: TopProduct[]
}


export interface CashierSalesSummary {
  sale_count: number
  revenue: number | string
}

export interface RecentSale {
  id: number
  receipt_number: string
  total_amount: number | string
  completed_at: string
}

export interface CashierDashboardData {
  date: string
  sales_summary: CashierSalesSummary
  payment_summary: PaymentSummary
  stock_summary: StockSummary
  recent_sales: RecentSale[]
}
