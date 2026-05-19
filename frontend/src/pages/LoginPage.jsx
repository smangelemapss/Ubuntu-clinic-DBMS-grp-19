import { useState, useEffect } from 'react'

import { Link, useNavigate, useLocation } from 'react-router-dom'

import {
  User,
  Lock,
  LogIn,
  Zap,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  Home,
} from 'lucide-react'

import { useAuth } from '../context/AuthContext'

import axiosInstance from '../api/axios/Instance'

import { APP_NAME } from '../constants/brand'

import BrandLogo from '../components/ui/BrandLogo'

import { getDashboardPath } from '../utils/authRoutes'

import './LoginPage.css'



const PORTAL_CONFIG = {

  patient: {

    subtitle: 'Patient Portal Sign In',

    demoUser: 'karabo.mabena',

    demoPass: 'Clinic@123',

    demoHint: 'Demo patient: karabo.mabena · Clinic@123',

    showRegister: true,

    switchLabel: 'Clinic staff?',

    switchTo: '/staff/login',

    switchText: 'Staff sign in',

  },

  staff: {

    subtitle: 'Clinic Staff Sign In',

    demoUser: 'dr.mokoena',

    demoPass: 'Clinic@123',

    demoHint: 'Demo: dr.mokoena (doctor) · nurse.molefe (nurse) · admin.ndlovu (admin) · Password: Clinic@123',

    showRegister: false,

    switchLabel: 'Student patient?',

    switchTo: '/login',

    switchText: 'Patient portal sign in',

  },

}



export default function LoginPage({ portal = 'patient' }) {

  const config = PORTAL_CONFIG[portal] || PORTAL_CONFIG.patient

  const [username, setUsername] = useState('')

  const [password, setPassword] = useState('')

  const [loading, setLoading] = useState(false)

  const [error, setError] = useState('')

  const [success, setSuccess] = useState('')

  const [apiStatus, setApiStatus] = useState('checking')

  const navigate = useNavigate()

  const location = useLocation()

  const { login } = useAuth()



  useEffect(() => {

    if (location.state?.registered) {

      setSuccess(`Account created for ${location.state.registered}. Sign in below.`)

      window.history.replaceState({}, document.title)

    }

  }, [location.state])



  useEffect(() => {

    axiosInstance

      .get('/api/v1/health/')

      .then((res) => {

        setApiStatus(res.data?.database === 'connected' ? 'connected' : 'degraded')

      })

      .catch(() => setApiStatus('offline'))

  }, [])



  const performLogin = async (trimmedUsername, trimmedPassword) => {

    const response = await axiosInstance.post('/api/v1/auth/login/', {

      username: trimmedUsername,

      password: trimmedPassword,

    })



    const { access, refresh, role, user } = response.data || {}



    if (!access || !user) {

      setError('Login response was incomplete. Restart the backend (python app.py) and try again.')

      return false

    }



    const userRole = role || user.role



    if (portal === 'patient' && userRole !== 'PATIENT') {

      setError('This page is for patients. Use staff sign in for clinic accounts.')

      return false

    }



    if (portal === 'staff' && userRole === 'PATIENT') {

      setError('Patient accounts must use the patient portal sign in.')

      return false

    }



    localStorage.setItem('access_token', access)

    localStorage.setItem('refresh_token', refresh)

    await login({ ...user, role: userRole })

    navigate(getDashboardPath(userRole), { replace: true })

    return true

  }



  const handleSubmit = async (e) => {

    e.preventDefault()

    setLoading(true)

    setError('')

    setSuccess('')



    if (apiStatus === 'offline') {

      setError('Backend is not running. Open a CMD window, cd backend, run: python app.py')

      setLoading(false)

      return

    }



    let trimmedUsername = username.trim().toLowerCase()

    const trimmedPassword = password.trim()



    if (trimmedUsername.includes(' ')) {

      trimmedUsername = trimmedUsername.split(/\s+/).join('.')

    }



    if (!trimmedUsername.includes('.')) {

      setError('Enter the full username: karabo.mabena (you typed only part of it).')

      setLoading(false)

      return

    }



    try {

      await performLogin(trimmedUsername, trimmedPassword)

    } catch (err) {

      if (!err.response) {

        setError(

          'Cannot reach the API. Start the backend with: python app.py (in the backend folder).'

        )

      } else if (err.response?.data?.code === 'SEED_PASSWORDS_NOT_CONFIGURED') {

        setError(err.response.data.error)

      } else if (err.response?.status === 401) {

        setError('Invalid username or password.')

      } else {

        setError(err.response?.data?.error || 'Login failed. Please try again.')

      }

    } finally {

      setLoading(false)

    }

  }



  const handleDemoLogin = async () => {

    if (apiStatus === 'offline') {

      setError('Backend is not running. Run python app.py in the backend folder.')

      return

    }

    setError('')

    setSuccess('')

    setLoading(true)

    setUsername(config.demoUser)

    setPassword(config.demoPass)

    try {

      await performLogin(config.demoUser, config.demoPass)

    } catch (err) {

      setError(

        err.response?.data?.error

          || (err.response ? 'Login failed.' : 'Cannot reach API — run python app.py in backend folder.')

      )

    } finally {

      setLoading(false)

    }

  }



  const statusConfig = {

    checking: { class: 'alert-muted', Icon: Loader2, spin: true, text: 'Checking API connection...' },

    connected: { class: 'alert-success', Icon: CheckCircle2, text: 'API and database connected' },

    degraded: { class: 'alert-warning', Icon: AlertTriangle, text: 'API running but database unavailable' },

    offline: { class: 'alert-error', Icon: XCircle, text: 'Backend offline — run python app.py' },

  }

  const status = statusConfig[apiStatus] || statusConfig.checking

  const StatusIcon = status.Icon



  return (

    <div className="auth-shell login-page">
      <div className="auth-shell__bg" aria-hidden="true" />
      <div className="auth-shell__inner">
        <div className="auth-top-bar">
          <Link to="/" className="auth-top-bar__home">
            <Home size={16} aria-hidden="true" />
            Homepage
          </Link>
          <span className="auth-top-bar__badge">
            {portal === 'staff' ? 'Staff portal' : 'Patient portal'}
          </span>
        </div>
        <div className="login-card">

        <div className="login-card__accent" />

        <div className="login-card__body">

          <header className="login-brand">

            <Link to="/" className="login-brand__home-link">

              <BrandLogo size="lg" />

            </Link>

            <p className="login-brand__subtitle">{config.subtitle}</p>

            <Link to="/" className="login-back-home">

              Back to homepage

            </Link>

          </header>



          <div className={`alert ${status.class} login-alert-row`}>

            <StatusIcon

              size={18}

              className={status.spin ? 'spin-icon' : undefined}

              aria-hidden="true"

            />

            <span>{status.text}</span>

          </div>



          {success && (

            <div className="alert alert-success login-alert-row">

              <CheckCircle2 size={18} aria-hidden="true" />

              <span>{success}</span>

            </div>

          )}



          {error && (

            <div className="alert alert-error login-alert-row">

              <XCircle size={18} aria-hidden="true" />

              <span>{error}</span>

            </div>

          )}



          <form className="login-form" onSubmit={handleSubmit}>

            <div className="form-group">

              <label htmlFor="username">Username</label>

              <div className="input-icon-row">

                <User size={18} aria-hidden="true" />

                <input

                  id="username"

                  type="text"

                  value={username}

                  onChange={(e) => setUsername(e.target.value)}

                  required

                  placeholder={config.demoUser}

                  autoComplete="username"

                />

              </div>

            </div>



            <div className="form-group">

              <label htmlFor="password">Password</label>

              <div className="input-icon-row">

                <Lock size={18} aria-hidden="true" />

                <input

                  id="password"

                  type="password"

                  value={password}

                  onChange={(e) => setPassword(e.target.value)}

                  required

                  placeholder="Enter password"

                />

              </div>

            </div>



            <div className="login-actions">

              <button type="submit" disabled={loading} className="btn btn-primary">

                {loading ? (

                  <Loader2 size={18} className="spin-icon" aria-hidden="true" />

                ) : (

                  <LogIn size={18} aria-hidden="true" />

                )}

                {loading ? 'Signing in...' : 'Sign in'}

              </button>

              <button

                type="button"

                disabled={loading || apiStatus === 'offline'}

                className="btn btn-secondary"

                onClick={handleDemoLogin}

              >

                <Zap size={18} aria-hidden="true" />

                One-click demo login

              </button>

            </div>

          </form>



          <p className="login-demo-note">

            {config.demoHint}

          </p>



          <p className="login-portal-switch">

            {config.switchLabel}{' '}

            <Link to={config.switchTo}>{config.switchText}</Link>

          </p>



          {config.showRegister && (

            <p className="login-portal-switch">

              New patient? <Link to="/register">Create an account</Link>

            </p>

          )}



          {!config.showRegister && (

            <p className="login-portal-switch login-portal-switch--muted">

              Staff accounts are created by your clinic administrator — no public registration.

            </p>

          )}



          <p className="login-footer">

            {APP_NAME} &copy; {new Date().getFullYear()}

          </p>

        </div>

        </div>
      </div>
    </div>
  )

}


