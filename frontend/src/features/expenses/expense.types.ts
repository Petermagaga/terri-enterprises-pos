
export type ExpenseType = 'SETUP' | 'OPERATING' | 'CAPITAL'

export type CostBehaviour = 'FIXED' | 'VARIABLE' | 'SEMI_VARIABLE'

export type ExpenseCategory =
  // Setup costs
  | 'BUSINESS_REGISTRATION'
  | 'LICENSES_PERMITS'
  | 'INITIAL_RENT_DEPOSIT'
  | 'SHOP_RENOVATION'
  | 'SHELVES_DISPLAY_SETUP'
  | 'REFRIGERATION_SETUP'
  | 'INITIAL_STOCK_ARRANGEMENT'
  | 'INITIAL_MARKETING'
  | 'STAFF_TRAINING'
  | 'UTILITY_CONNECTIONS'

  // Operating costs
  | 'RENT'
  | 'ELECTRICITY'
  | 'WATER'
  | 'INTERNET'
  | 'SALARIES_WAGES'
  | 'FUEL_TRANSPORT'
  | 'LOADING_OFFLOADING'
  | 'MAINTENANCE_REPAIRS'
  | 'CLEANING'
  | 'SECURITY'
  | 'MARKETING_ADVERTISING'
  | 'INSURANCE'
  | 'PACKAGING_MATERIALS'
  | 'SHOP_SUPPLIES'
  | 'TELEPHONE_AIRTIME'
  | 'BANK_CHARGES'
  | 'WASTE_COLLECTION'
  | 'MISCELLANEOUS'

  // Capital expenses
  | 'LAND'
  | 'BUILDING'
  | 'MOTOR_VEHICLE'
  | 'REFRIGERATORS_FREEZERS'
  | 'SHELVING_DISPLAY_EQUIPMENT'
  | 'CHECKOUT_COUNTERS'
  | 'POS_EQUIPMENT'
  | 'COMPUTERS_LAPTOPS'
  | 'PRINTERS'
  | 'CCTV_SECURITY'
  | 'GENERATORS_BACKUP'
  | 'WEIGHING_SCALES'
  | 'MACHINERY_EQUIPMENT'
  | 'SOFTWARE_LICENSES'

  | 'OTHER'

export type ExpensePaymentMethod =
  | 'CASH'
  | 'MPESA'
  | 'BANK_TRANSFER'
  | 'CHEQUE'
  | 'CREDIT_CARD'

export interface Expense {
  id: number
  expense_type: ExpenseType
  category: ExpenseCategory
  custom_category: string
  cost_behaviour: CostBehaviour
  description: string
  payee: string
  amount: string
  expense_date: string
  payment_method: ExpensePaymentMethod
  payment_reference: string
  is_recurring: boolean
  recorded_by: number
  recorded_by_username: string
  created_at: string
  updated_at: string
}

export interface CreateExpensePayload {
  expense_type: ExpenseType
  category: ExpenseCategory
  custom_category: string
  cost_behaviour: CostBehaviour
  description: string
  payee: string
  amount: string
  expense_date: string
  payment_method: ExpensePaymentMethod
  payment_reference: string
  is_recurring: boolean
}

export type UpdateExpensePayload = Partial<CreateExpensePayload>
