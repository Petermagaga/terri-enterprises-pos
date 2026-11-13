
import { createBrowserRouter, Navigate } from 'react-router-dom'

import ProtectedRoute from '../auth/ProtectedRoute'
import AppLayout from '../components/layout/AppLayout'

import {
  LoginPage,
  OwnerDashboardPage,
  CashierDashboardPage,
  SalesPage,
  SalesHistoryPage,
  ProductsPage,
  CatalogueSetupPage,
  InventoryPage,
  ExpensesPage,
  SuppliersPage,
  ProfitLossPage,
  ProductProfitabilityPage,
  PaymentSummaryPage,
  SalesSummaryPage,
  CashiersPage,
} from './routePages'

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
    element: (
      <h1>
        Access denied. You do not have permission to view this page.
      </h1>
    ),
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
