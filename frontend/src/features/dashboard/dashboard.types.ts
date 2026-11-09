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

export interface OwnerDashboardData {
  date: string
  financial_summary: FinancialSummary
  payment_summary: PaymentSummary
  sales_summary: SalesSummary
  stock_summary: StockSummary
  top_products: unknown[]
}