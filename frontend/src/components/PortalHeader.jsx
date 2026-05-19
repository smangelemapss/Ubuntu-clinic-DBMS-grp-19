import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Home, LogOut, Menu, X, ChevronRight } from 'lucide-react'
import BrandLogo from './ui/BrandLogo'

export default function PortalHeader({ brandTo, navItems = [], userLabel, onLogout }) {
  const [mobileOpen, setMobileOpen] = useState(false)

  const linkClass = ({ isActive }) =>
    `portal-header__nav-link${isActive ? ' portal-header__nav-link--active' : ''}`

  return (
    <header className="portal-header">
      <div className="portal-header__shell">
        <Link to={brandTo} className="portal-header__brand" onClick={() => setMobileOpen(false)}>
          <BrandLogo size="md" />
        </Link>

        {navItems.length > 0 && (
          <nav className="portal-header__nav" aria-label="Portal navigation">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                className={linkClass}
                end={end}
                onClick={() => setMobileOpen(false)}
              >
                <Icon size={16} strokeWidth={2} aria-hidden="true" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
        )}

        <div className="portal-header__meta">
          {userLabel && <span className="portal-header__user-chip">{userLabel}</span>}
          <div className="portal-header__actions portal-header__actions--desktop">
            <Link to="/" className="portal-header__btn portal-header__btn--ghost">
              <Home size={16} aria-hidden="true" />
              <span>Home</span>
            </Link>
            <button
              type="button"
              onClick={onLogout}
              className="portal-header__btn portal-header__btn--danger"
            >
              <LogOut size={16} aria-hidden="true" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        <button
          type="button"
          className="portal-header__menu-btn"
          aria-expanded={mobileOpen}
          aria-controls="portal-mobile-nav"
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          onClick={() => setMobileOpen((o) => !o)}
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <div
        id="portal-mobile-nav"
        className={`portal-header__mobile ${mobileOpen ? 'portal-header__mobile--open' : ''}`}
      >
        {navItems.length > 0 && (
          <nav aria-label="Mobile portal navigation">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                className={linkClass}
                end={end}
                onClick={() => setMobileOpen(false)}
              >
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Icon size={18} aria-hidden="true" />
                  {label}
                </span>
                <ChevronRight size={18} aria-hidden="true" />
              </NavLink>
            ))}
          </nav>
        )}
        {userLabel && (
          <p className="portal-header__mobile-user" style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', fontWeight: 600, padding: '0 0.25rem' }}>
            {userLabel}
          </p>
        )}
        <div className="portal-header__actions portal-header__actions--stacked">
          <Link
            to="/"
            className="portal-header__btn portal-header__btn--ghost"
            style={{ width: '100%' }}
            onClick={() => setMobileOpen(false)}
          >
            <Home size={16} aria-hidden="true" />
            Homepage
          </Link>
          <button
            type="button"
            onClick={() => {
              setMobileOpen(false)
              onLogout()
            }}
            className="portal-header__btn portal-header__btn--danger"
            style={{ width: '100%' }}
          >
            <LogOut size={16} aria-hidden="true" />
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
