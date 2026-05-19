import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Calendar,
  FileText,
  Shield,
  Clock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  Stethoscope,
  Users,
  Sparkles,
  ChevronRight,
  HeartPulse,
  Menu,
  X,
  UserPlus,
  LogIn,
  BriefcaseMedical,
} from 'lucide-react'
import axiosInstance from '../api/axios/Instance'
import { APP_NAME, APP_TAGLINE } from '../constants/brand'
import BrandLogo from '../components/ui/BrandLogo'
import { useAuth } from '../context/AuthContext'
import { getDashboardPath } from '../utils/authRoutes'
import './HomePage.css'

const FEATURES = [
  {
    icon: Calendar,
    title: 'Book Appointments',
    description:
      'Choose your doctor, date, and time slot — in-person or virtual consultation.',
  },
  {
    icon: FileText,
    title: 'Medical History',
    description:
      'Access diagnoses, prescriptions, and visit records from past consultations.',
  },
  {
    icon: Clock,
    title: 'Track Visits',
    description:
      'View upcoming appointments, cancel when needed, and review your visit history.',
  },
  {
    icon: Shield,
    title: 'Emergency Contacts',
    description:
      'Keep trusted contacts on file for urgent situations at the clinic.',
  },
]

const STEPS = [
  {
    step: '01',
    title: 'Create your account',
    description: 'Register with your student details in under two minutes.',
  },
  {
    step: '02',
    title: 'Book a consultation',
    description: 'Pick a doctor, date, and slot that fits your schedule.',
  },
  {
    step: '03',
    title: 'Manage your care',
    description: 'View records, get reminders, and stay on top of your health.',
  },
]

const TRUST_STATS = [
  { value: '24/7', label: 'Portal access' },
  { value: '100%', label: 'Secure records' },
  { value: '< 2 min', label: 'Booking time' },
  { value: 'POPIA', label: 'Aligned privacy' },
]

const NAV_LINKS = [
  { href: '#features', label: 'Features' },
  { href: '#how-it-works', label: 'How it works' },
]

export default function HomePage() {
  const { user } = useAuth()
  const [apiStatus, setApiStatus] = useState('checking')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  useEffect(() => {
    axiosInstance
      .get('/api/v1/health/')
      .then((res) => {
        setApiStatus(res.data?.database === 'connected' ? 'connected' : 'degraded')
      })
      .catch(() => setApiStatus('offline'))
  }, [])

  const statusConfig = {
    checking: {
      class: 'home-status--muted',
      Icon: Loader2,
      spin: true,
      text: 'Checking system status…',
    },
    connected: {
      class: 'home-status--ok',
      Icon: CheckCircle2,
      text: 'All systems operational',
    },
    degraded: {
      class: 'home-status--warn',
      Icon: AlertTriangle,
      text: 'Limited service — database unavailable',
    },
    offline: {
      class: 'home-status--err',
      Icon: XCircle,
      text: 'Backend offline — start the API server',
    },
  }
  const status = statusConfig[apiStatus] || statusConfig.checking
  const StatusIcon = status.Icon

  const primaryCta = user ? (
    <Link to={getDashboardPath(user.role)} className="btn btn-primary btn-lg home-btn-hero">
      Open Dashboard
      <ArrowRight size={20} aria-hidden="true" />
    </Link>
  ) : (
    <>
      <Link to="/login" className="btn btn-primary btn-lg home-btn-hero">
        Patient sign in
        <ArrowRight size={20} aria-hidden="true" />
      </Link>
      <Link to="/register" className="btn btn-ghost btn-lg home-btn-hero-secondary">
        Create account
      </Link>
    </>
  )

  return (
    <div className="home-page">
      <div className="home-page__bg" aria-hidden="true">
        <div className="home-page__mesh" />
        <div className="home-page__grid" />
      </div>

      <header className="home-header">
        <div className="home-header__shell">
          <Link to="/" className="home-header__brand-card">
            <BrandLogo size="md" />
          </Link>
          <nav className="home-header__nav-card" aria-label="Primary">
            {NAV_LINKS.map(({ href, label }) => (
              <a key={href} href={href} className="home-header__nav-link">
                {label}
              </a>
            ))}
          </nav>
          <div className={`home-header__status-card home-status ${status.class}`} role="status">
            <StatusIcon
              size={15}
              className={status.spin ? 'spin-icon' : undefined}
              aria-hidden="true"
            />
            <span className="home-header__status-text">{status.text}</span>
          </div>
          <div className="home-header__actions-card">
            {user ? (
              <Link
                to={getDashboardPath(user.role)}
                className="home-header__btn home-header__btn--primary"
              >
                Dashboard
                <ArrowRight size={17} aria-hidden="true" />
              </Link>
            ) : (
              <>
                <Link to="/staff/login" className="home-header__btn home-header__btn--ghost">
                  <BriefcaseMedical size={16} aria-hidden="true" />
                  Staff
                </Link>
                <Link to="/register" className="home-header__btn home-header__btn--outline">
                  <UserPlus size={16} aria-hidden="true" />
                  Register
                </Link>
                <Link to="/login" className="home-header__btn home-header__btn--primary">
                  <LogIn size={16} aria-hidden="true" />
                  Sign in
                </Link>
              </>
            )}
          </div>

          <button
            type="button"
            className="home-header__menu-btn"
            aria-expanded={mobileNavOpen}
            aria-controls="home-mobile-nav"
            aria-label={mobileNavOpen ? 'Close menu' : 'Open menu'}
            onClick={() => setMobileNavOpen((open) => !open)}
          >
            {mobileNavOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        <div
          id="home-mobile-nav"
          className={`home-header__mobile ${mobileNavOpen ? 'home-header__mobile--open' : ''}`}
        >
          <nav className="home-header__mobile-nav" aria-label="Mobile">
            {NAV_LINKS.map(({ href, label }) => (
              <a
                key={href}
                href={href}
                className="home-header__mobile-link"
                onClick={() => setMobileNavOpen(false)}
              >
                {label}
                <ChevronRight size={18} aria-hidden="true" />
              </a>
            ))}
          </nav>
          <div className={`home-header__mobile-status home-status ${status.class}`}>
            <StatusIcon
              size={16}
              className={status.spin ? 'spin-icon' : undefined}
              aria-hidden="true"
            />
            <span>{status.text}</span>
          </div>
          <div className="home-header__mobile-actions">
            {user ? (
              <Link
                to={getDashboardPath(user.role)}
                className="home-header__btn home-header__btn--primary home-header__btn--block"
                onClick={() => setMobileNavOpen(false)}
              >
                Dashboard
                <ArrowRight size={18} aria-hidden="true" />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="home-header__btn home-header__btn--primary home-header__btn--block"
                  onClick={() => setMobileNavOpen(false)}
                >
                  <LogIn size={18} aria-hidden="true" />
                  Patient sign in
                </Link>
                <Link
                  to="/register"
                  className="home-header__btn home-header__btn--outline home-header__btn--block"
                  onClick={() => setMobileNavOpen(false)}
                >
                  <UserPlus size={18} aria-hidden="true" />
                  Create account
                </Link>
                <Link
                  to="/staff/login"
                  className="home-header__btn home-header__btn--ghost home-header__btn--block"
                  onClick={() => setMobileNavOpen(false)}
                >
                  <BriefcaseMedical size={18} aria-hidden="true" />
                  Staff portal
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <section className="home-hero" aria-labelledby="hero-heading">
        <div className="home-hero__content">
          <div className="home-hero__badge">
            <Sparkles size={14} aria-hidden="true" />
            <span>{APP_TAGLINE}</span>
          </div>

          <h1 id="hero-heading" className="home-hero__title">
            Campus healthcare,
            <span className="home-hero__title-accent"> designed for students</span>
          </h1>

          <p className="home-hero__lead">
            {APP_NAME} connects you to campus clinic services — book visits, access
            records, and manage your health in one secure, always-available portal.
          </p>

          <div className="home-hero__cta-card">
            <p className="home-hero__cta-label">Get started</p>
            <div className="home-hero__cta">{primaryCta}</div>
          </div>

          <ul className="home-hero__trust" aria-label="Key benefits">
            <li className="home-hero__trust-card">
              <span className="home-hero__trust-icon">
                <CheckCircle2 size={18} aria-hidden="true" />
              </span>
              <span className="home-hero__trust-text">HIPAA-style privacy controls</span>
            </li>
            <li className="home-hero__trust-card">
              <span className="home-hero__trust-icon">
                <CheckCircle2 size={18} aria-hidden="true" />
              </span>
              <span className="home-hero__trust-text">Real-time appointment slots</span>
            </li>
            <li className="home-hero__trust-card">
              <span className="home-hero__trust-icon">
                <CheckCircle2 size={18} aria-hidden="true" />
              </span>
              <span className="home-hero__trust-text">Staff & patient portals</span>
            </li>
          </ul>
        </div>

        <div className="home-hero__visual" aria-hidden="true">
          <div className="home-showcase">
            <div className="home-showcase__backdrop" />
            <div className="home-showcase__panel">
              <header className="home-showcase__header">
                <div className="home-showcase__brand">
                  <span className="home-showcase__logo">
                    <HeartPulse size={18} strokeWidth={2.25} />
                  </span>
                  <div>
                    <p className="home-showcase__app">{APP_NAME}</p>
                    <p className="home-showcase__role">Patient dashboard</p>
                  </div>
                </div>
                <span className="home-showcase__session">
                  <span className="home-showcase__session-dot" />
                  Secure session
                </span>
              </header>
              <div className="home-showcase__metrics">
                <article className="home-showcase__metric">
                  <Calendar size={18} aria-hidden="true" />
                  <div>
                    <span className="home-showcase__metric-label">Next appointment</span>
                    <strong>Tuesday · 10:30</strong>
                  </div>
                </article>
                <article className="home-showcase__metric home-showcase__metric--highlight">
                  <Stethoscope size={18} aria-hidden="true" />
                  <div>
                    <span className="home-showcase__metric-label">Assigned clinician</span>
                    <strong>Dr. Mokoena</strong>
                  </div>
                </article>
              </div>
              <div className="home-showcase__section">
                <div className="home-showcase__section-head">
                  <h3>Upcoming visits</h3>
                  <span>2 scheduled</span>
                </div>
                <ul className="home-showcase__agenda">
                  <li>
                    <div className="home-showcase__agenda-main">
                      <span className="home-showcase__tag home-showcase__tag--confirmed">Confirmed</span>
                      <p>General check-up</p>
                    </div>
                    <ChevronRight size={16} aria-hidden="true" />
                  </li>
                  <li>
                    <div className="home-showcase__agenda-main">
                      <span className="home-showcase__tag home-showcase__tag--pending">Pending</span>
                      <p>Lab results review</p>
                    </div>
                    <ChevronRight size={16} aria-hidden="true" />
                  </li>
                </ul>
              </div>
              <footer className="home-showcase__footer">
                <div className="home-showcase__assurance">
                  <Users size={16} aria-hidden="true" />
                  <span>Campus-wide student access</span>
                </div>
                <div className="home-showcase__assurance">
                  <Shield size={16} aria-hidden="true" />
                  <span>Encrypted health records</span>
                </div>
              </footer>
            </div>
          </div>

        </div>
      </section>

      <section className="home-stats" aria-label="Platform highlights">
        {TRUST_STATS.map(({ value, label }) => (
          <div key={label} className="home-stats__item">
            <span className="home-stats__value">{value}</span>
            <span className="home-stats__label">{label}</span>
          </div>
        ))}
      </section>

      <section id="features" className="home-features">
        <div className="home-section-head">
          <p className="home-section-eyebrow">Patient portal</p>
          <h2 className="home-section-title">Everything you need in one place</h2>
          <p className="home-section-desc">
            From booking to records — built for students who need fast, reliable campus
            healthcare without the paperwork.
          </p>
        </div>
        <div className="home-features__grid">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <article key={title} className="home-feature">
              <div className="home-feature__icon">
                <Icon size={22} strokeWidth={2} />
              </div>
              <h3>{title}</h3>
              <p>{description}</p>
              <span className="home-feature__link">
                Learn more <ChevronRight size={14} aria-hidden="true" />
              </span>
            </article>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="home-steps">
        <div className="home-section-head home-section-head--light">
          <p className="home-section-eyebrow home-section-eyebrow--light">How it works</p>
          <h2 className="home-section-title home-section-title--light">
            Three steps to better care
          </h2>
        </div>
        <ol className="home-steps__list">
          {STEPS.map(({ step, title, description }) => (
            <li key={step} className="home-step">
              <span className="home-step__num">{step}</span>
              <h3>{title}</h3>
              <p>{description}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="home-cta-band">
        <div className="home-cta-band__inner">
          <h2>Ready to take control of your campus health?</h2>
          <p>
            Join students using {APP_NAME} for appointments, records, and peace of mind.
          </p>
          <div className="home-cta-band__actions">
            {user ? (
              <Link to={getDashboardPath(user.role)} className="btn btn-primary btn-lg">
                Go to Dashboard
                <ArrowRight size={20} aria-hidden="true" />
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">
                  Get started free
                  <ArrowRight size={20} aria-hidden="true" />
                </Link>
                <Link to="/staff/login" className="btn btn-ghost btn-lg home-cta-band__staff">
                  Staff portal
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <footer className="home-footer">
        <BrandLogo size="sm" showTagline={false} />
        <p>
          {APP_NAME} &copy; {new Date().getFullYear()} · Group 19 · CMPG 311
        </p>
      </footer>
    </div>
  )
}
