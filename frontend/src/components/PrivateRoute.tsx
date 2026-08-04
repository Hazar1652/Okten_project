import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../store/authContext'

export default function PrivateRoute() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) return <p className="muted">Завантаження...</p>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Outlet />
}
