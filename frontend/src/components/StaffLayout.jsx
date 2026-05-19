import { Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PortalHeader from './PortalHeader'
import { roleLabel } from '../utils/authRoutes'
import '../styles/portal-shell.css'

export default function StaffLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/staff/login')
  }

  const userLabel = user
    ? `${roleLabel(user.role)} · ${user.username}`
    : 'Staff portal'

  return (
    <div className="portal-shell layout">
      <div className="portal-shell__bg" aria-hidden="true" />
      <PortalHeader
        brandTo="/staff/dashboard"
        userLabel={userLabel}
        onLogout={handleLogout}
      />
      <main className="portal-main">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
