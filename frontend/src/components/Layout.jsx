import { Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Phone,
  Calendar,
  CalendarPlus,
  User,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import PortalHeader from './PortalHeader'
import '../styles/portal-shell.css'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/medical-history', label: 'History', icon: FileText },
  { to: '/emergency-contacts', label: 'Contacts', icon: Phone },
  { to: '/appointments', label: 'Appointments', icon: Calendar },
  { to: '/book-appointment', label: 'Book', icon: CalendarPlus },
  { to: '/profile', label: 'Profile', icon: User },
]

const Layout = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const userLabel = user?.username ? `Patient · ${user.username}` : 'Patient portal'

  return (
    <div className="portal-shell layout">
      <div className="portal-shell__bg" aria-hidden="true" />
      <PortalHeader
        brandTo="/dashboard"
        navItems={NAV_ITEMS}
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

export default Layout
