
import { lazy } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'

import ProtectedRoute from '../auth/ProtectedRoute'
import AppLayout from '../components/layout/AppLayout'

// Lazy-loaded pages
const LoginPage = lazy(() => import('../pages/LoginPage'))
const OwnerDashboardPage = lazy(
  () => import('../features/dashboard/OwnerDashboardPage'),
)
const CashierDashboardPage = lazy(
  () => import('../features/dashboard/CashierDashboardPage'),
)
const SalesPage = lazy(() => import('../features/sales/salesPage'))
const SalesHistoryPage = lazy(
  () => import('../features/sales/SalesHistoryPage'),
)
const ProductsPage = lazy(
  () => import('../features/products/ProductsPage'),
)
const CatalogueSetupPage = lazy(
  () => import('../features/products/CatalogueSetupPage'),
)
const InventoryPage = lazy(
  () => import('../features/inventory/InventoryPage'),
)
const ExpensesPage = lazy(
  () => import('../features/expenses/ExpensesPage'),
)
const SuppliersPage = lazy(
  () => import('../features/suppliers/suppliersPage'),
)
const ProfitLossPage = lazy(
  () => import('../features/reports/ProfitLossPage'),
)
const ProductProfitabilityPage = lazy(
  () => import('../features/reports/ProductProfitabilityPage'),
)
const PaymentSummaryPage = lazy(
  () => import('../features/reports/PaymentSummaryPage'),
)
const SalesSummaryPage = lazy(
  () => import('../features/reports/SalesSummaryPage'),
)
const CashiersPage = lazy(
  () => import('../features/cashiers/CashiersPage'),
)

function UnauthorizedPage() {
  return (
    <h1>
      Access denied. You do not have permission to view this page.
    </h1>
  )
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/unauthorized',
    element: <UnauthorizedPage />,
  },
  {
    element: <ProtectedRoute allowedRoles={['OWNER']} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/owner', element: <OwnerDashboardPage /> },
          { path: '/products', element: <ProductsPage /> },
          { path: '/catalogue-setup', element: <CatalogueSetupPage /> },
          { path: '/inventory', element: <InventoryPage /> },
          { path: '/suppliers', element: <SuppliersPage /> },
          { path: '/expenses', element: <ExpensesPage /> },
          { path: '/reports', element: <ProfitLossPage /> },
          {
            path: '/product-profitability',
            element: <ProductProfitabilityPage />,
          },
          {
            path: '/payment-summary',
            element: <PaymentSummaryPage />,
          },
          {
            path: '/sales-summary',
            element: <SalesSummaryPage />,
          },
          { path: '/cashiers', element: <CashiersPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute allowedRoles={['OWNER', 'CASHIER']} />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/cashier', element: <CashierDashboardPage /> },
          { path: '/sales', element: <SalesPage /> },
          { path: '/sales-history', element: <SalesHistoryPage /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])
