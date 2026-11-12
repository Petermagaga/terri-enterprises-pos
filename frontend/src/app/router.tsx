import SalesHistoryPage from '../features/sales/SalesHistoryPage'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import ProductsPage from '../features/products/ProductsPage'
import ProtectedRoute from '../auth/ProtectedRoute'
import AppLayout from '../components/layout/AppLayout'
import LoginPage from '../pages/LoginPage'
import OwnerDashboardPage from '../features/dashboard/OwnerDashboardPage'
import CashierDashboardPage from '../features/dashboard/CashierDashboardPage'
import SalesPage from '../features/sales/salesPage'
import CatalogueSetupPage from '../features/products/CatalogueSetupPage'
import InventoryPage from '../features/inventory/InventoryPage'
import ExpensesPage from '../features/expenses/ExpensesPage'
import SuppliersPage from '../features/suppliers/suppliersPage'
import ProfitLossPage from '../features/reports/ProfitLossPage'
import ProductProfitabilityPage from '../features/reports/ProductProfitabilityPage'
import PaymentSummaryPage from '../features/reports/PaymentSummaryPage'
import SalesSummaryPage from '../features/reports/SalesSummaryPage'


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

          {
            path: '/cashier',
            element: <CashierDashboardPage />,
          },

          {
            path: '/sales',
            element: <SalesPage />,
          },
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
