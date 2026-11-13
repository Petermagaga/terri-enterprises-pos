import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './useAuth'
interface ProtectedRouteProps {
  allowedRoles?: ('OWNER' | 'CASHIER')[]
}

export default function ProtectedRoute({
  allowedRoles,
}: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div>Loading your session...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />
  }

  return <Outlet />
}