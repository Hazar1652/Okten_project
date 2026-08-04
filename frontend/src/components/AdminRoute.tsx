import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../store/authContext'

export default function AdminRoute() {
  const { isSuperAdmin, loading, isAuthenticated } = useAuth()

  if (loading) return <p className="muted">Завантаження...</p>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!isSuperAdmin) return <Navigate to="/" replace />
  return <Outlet />
}
