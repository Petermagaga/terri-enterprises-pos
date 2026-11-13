
import { lazy } from 'react'

export const LoginPage = lazy(() => import('../pages/LoginPage'))

export const OwnerDashboardPage = lazy(
  () => import('../features/dashboard/OwnerDashboardPage'),
)

export const CashierDashboardPage = lazy(
  () => import('../features/dashboard/CashierDashboardPage'),
)

export const SalesPage = lazy(() => import('../features/sales/salesPage'))

export const SalesHistoryPage = lazy(
  () => import('../features/sales/SalesHistoryPage'),
)

export const ProductsPage = lazy(
  () => import('../features/products/ProductsPage'),
)

export const CatalogueSetupPage = lazy(
  () => import('../features/products/CatalogueSetupPage'),
)

export const InventoryPage = lazy(
  () => import('../features/inventory/InventoryPage'),
)

export const ExpensesPage = lazy(
  () => import('../features/expenses/ExpensesPage'),
)

export const SuppliersPage = lazy(
  () => import('../features/suppliers/suppliersPage'),
)

export const ProfitLossPage = lazy(
  () => import('../features/reports/ProfitLossPage'),
)

export const ProductProfitabilityPage = lazy(
  () => import('../features/reports/ProductProfitabilityPage'),
)

export const PaymentSummaryPage = lazy(
  () => import('../features/reports/PaymentSummaryPage'),
)

export const SalesSummaryPage = lazy(
  () => import('../features/reports/SalesSummaryPage'),
)

export const CashiersPage = lazy(
  () => import('../features/cashiers/CashiersPage'),
)
