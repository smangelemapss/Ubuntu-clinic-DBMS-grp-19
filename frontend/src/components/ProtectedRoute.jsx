import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import BrandLogo from './ui/BrandLogo'
import { APP_NAME } from '../constants/brand'
import { getDashboardPath } from '../utils/authRoutes'

function staffLoginPath(pathname) {
  return pathname.startsWith('/staff') || pathname.startsWith('/admin')
}

export default function ProtectedRoute({ roles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="app-loading">
        <BrandLogo size="lg" className="app-loading__brand" />
        <div className="app-loading__spinner" aria-hidden="true" />
        <p>Loading {APP_NAME}...</p>
      </div>
    )
  }

  if (!user) {
    const loginTo = staffLoginPath(location.pathname) ? '/staff/login' : '/login'
    return <Navigate to={loginTo} replace state={{ from: location.pathname }} />
  }

  if (roles?.length && !roles.includes(user.role)) {
    return <Navigate to={getDashboardPath(user.role)} replace />
  }

  return <Outlet />
}
