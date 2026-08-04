import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../store/authContext'

/** Будь-який залогінений користувач може керувати своїми закладами. */
export default function ManagerRoute() {
  const { loading, isAuthenticated } = useAuth()

  if (loading) return <p className="muted">Завантаження...</p>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Outlet />
}
