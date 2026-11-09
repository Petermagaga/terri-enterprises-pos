
import { createBrowserRouter, Navigate } from 'react-router-dom'
import ProductsPage from '../features/products/ProductsPage'
import ProtectedRoute from '../auth/ProtectedRoute'
import AppLayout from '../components/layout/AppLayout'
import LoginPage from '../pages/LoginPage'
import OwnerDashboardPage from '../features/dashboard/OwnerDashboardPage'
import SalesPage from '../features/sales/salesPage'
import CatalogueSetupPage from '../features/products/CatalogueSetupPage'

function UnauthorizedPage() {
  return (
    <h1>
      Access denied. You do not have permission to view this page.
    </h1>
  )
}

function CashierDashboard() {
  return <h1>Cashier Dashboard</h1>
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
            element: <CashierDashboard />,
          },
          {
            path: '/sales',
            element: <SalesPage />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])
