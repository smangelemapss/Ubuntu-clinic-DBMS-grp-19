import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, Lock, Mail, Hash, UserPlus, Loader2, XCircle, Home } from 'lucide-react'
import { registerPatient, getApiError } from '../services/api'
import { APP_NAME } from '../constants/brand'
import BrandLogo from '../components/ui/BrandLogo'
import {
  expectedNwuEmail,
  validateNwuEmail,
  validatePassword,
  validateStudentNumber,
  validateUsername,
} from '../utils/registrationValidation'
import './LoginPage.css'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [studentNumber, setStudentNumber] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleStudentNumberChange = (value) => {
    const digitsOnly = value.replace(/\D/g, '').slice(0, 8)
    setStudentNumber(digitsOnly)
    const trimmedEmail = email.trim().toLowerCase()
    if (!trimmedEmail || /^(\d{0,8})@mynwu\.ac\.za$/i.test(trimmedEmail)) {
      setEmail(digitsOnly ? expectedNwuEmail(digitsOnly) : '')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const { error: usernameError, username: trimmedUsername } = validateUsername(username)
    if (usernameError) {
      setError(usernameError)
      return
    }

    const trimmedStudentNumber = studentNumber.trim()
    const studentError = validateStudentNumber(trimmedStudentNumber)
    if (studentError) {
      setError(studentError)
      return
    }

    const trimmedEmail = email.trim().toLowerCase()
    const emailError = validateNwuEmail(trimmedEmail, trimmedStudentNumber)
    if (emailError) {
      setError(emailError)
      return
    }

    const passwordError = validatePassword(password)
    if (passwordError) {
      setError(passwordError)
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    try {
      await registerPatient({
        username: trimmedUsername,
        student_number: trimmedStudentNumber,
        email: trimmedEmail,
        password,
      })
      navigate('/login', {
        replace: true,
        state: { registered: trimmedUsername },
      })
    } catch (err) {
      setError(getApiError(err, 'Registration failed. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell login-page">
      <div className="auth-shell__bg" aria-hidden="true" />
      <div className="auth-shell__inner">
        <div className="auth-top-bar">
          <Link to="/" className="auth-top-bar__home">
            <Home size={16} aria-hidden="true" />
            Homepage
          </Link>
          <span className="auth-top-bar__badge">New patient</span>
        </div>
        <div className="login-card">
        <div className="login-card__accent" />
        <div className="login-card__body">
          <header className="login-brand">
            <Link to="/" className="login-brand__home-link">
              <BrandLogo size="lg" />
            </Link>
            <p className="login-brand__subtitle">Create your patient account</p>
            <Link to="/" className="login-back-home">
              Back to homepage
            </Link>
          </header>

          {error && (
            <div className="alert alert-error login-alert-row">
              <XCircle size={18} aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="reg-username">Username</label>
              <div className="input-icon-row">
                <User size={18} aria-hidden="true" />
                <input
                  id="reg-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  placeholder="firstname.lastname"
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="reg-student-number">Student number</label>
              <div className="input-icon-row">
                <Hash size={18} aria-hidden="true" />
                <input
                  id="reg-student-number"
                  type="text"
                  inputMode="numeric"
                  pattern="\d{8}"
                  value={studentNumber}
                  onChange={(e) => handleStudentNumberChange(e.target.value)}
                  required
                  maxLength={8}
                  placeholder="e.g. 48277444"
                  autoComplete="off"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="reg-email">Email</label>
              <div className="input-icon-row">
                <Mail size={18} aria-hidden="true" />
                <input
                  id="reg-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="48277444@mynwu.ac.za"
                  autoComplete="email"
                />
              </div>
              <p className="form-hint">Use your official NWU student email (@mynwu.ac.za).</p>
            </div>

            <div className="form-group">
              <label htmlFor="reg-password">Password</label>
              <div className="input-icon-row">
                <Lock size={18} aria-hidden="true" />
                <input
                  id="reg-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  placeholder="8+ chars, letter and number"
                  autoComplete="new-password"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="reg-confirm">Confirm password</label>
              <div className="input-icon-row">
                <Lock size={18} aria-hidden="true" />
                <input
                  id="reg-confirm"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  placeholder="Repeat password"
                  autoComplete="new-password"
                />
              </div>
            </div>

            <div className="login-actions">
              <button type="submit" disabled={loading} className="btn btn-primary">
                {loading ? (
                  <Loader2 size={18} className="spin-icon" aria-hidden="true" />
                ) : (
                  <UserPlus size={18} aria-hidden="true" />
                )}
                {loading ? 'Creating account...' : 'Create account'}
              </button>
            </div>
          </form>

          <p className="login-portal-switch">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
          <p className="login-portal-switch login-portal-switch--muted">
            Clinic staff are added by an administrator —{' '}
            <Link to="/staff/login">staff sign in</Link>
          </p>

          <p className="login-footer">
            {APP_NAME} &copy; {new Date().getFullYear()}
          </p>
        </div>
        </div>
      </div>
    </div>
  )
}
