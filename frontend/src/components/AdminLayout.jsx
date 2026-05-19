import { Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PortalHeader from './PortalHeader'
import '../styles/portal-shell.css'

export default function AdminLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/staff/login')
  }

  const userLabel = user ? `Admin · ${user.username}` : 'Administration'

  return (
    <div className="portal-shell layout">
      <div className="portal-shell__bg" aria-hidden="true" />
      <PortalHeader
        brandTo="/admin/dashboard"
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
