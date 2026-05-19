import { useState, useEffect } from 'react'
import { Hash, Pencil, Save, X, QrCode, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getPatientProfile, updatePatientProfile, getPatientQrCode, getApiError } from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'

const PatientProfile = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [qrData, setQrData] = useState(null)
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    address: '',
  })
  const [patientId, setPatientId] = useState('')

  useEffect(() => {
    loadProfile()
  }, [user])

  const loadProfile = async () => {
    setLoading(true)
    setError('')
    try {
      const profile = await getPatientProfile()
      setPatientId(profile.patient_id || profile.student_number || '')
      setFormData({
        firstName: profile.first_name || '',
        lastName: profile.last_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
        dateOfBirth: profile.date_of_birth || '',
        address: profile.address || '',
      })
      const qr = await getPatientQrCode()
      setQrData(qr)
    } catch (err) {
      setPatientId(user?.patient_id || user?.id || '')
      setFormData({
        firstName: user?.first_name || '',
        lastName: user?.last_name || '',
        email: user?.email || '',
        phone: user?.phone || '',
        dateOfBirth: user?.date_of_birth || '',
        address: user?.address || '',
      })
      setError(getApiError(err, 'Could not load profile.'))
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      await updatePatientProfile(formData)
      setSuccess('Profile saved successfully.')
      setIsEditing(false)
      await loadProfile()
    } catch (err) {
      setError(getApiError(err, 'Failed to save profile.'))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <PageLoading message="Loading profile..." />
  }

  return (
    <>
      <PageHeader
        eyebrow="Your account"
        icon={User}
        title="My profile"
        subtitle="Personal details, contact information, and your clinic check-in QR code."
      />

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="card card--elevated">
        <div className="profile-header">
          <div className="profile-avatar" aria-hidden="true">
            {(formData.firstName[0] || '?').toUpperCase()}
            {(formData.lastName[0] || '').toUpperCase()}
          </div>
          <div>
            <h2 className="profile-name">
              {formData.firstName} {formData.lastName}
            </h2>
            <p className="profile-id">
              <Hash size={14} aria-hidden="true" />
              Patient ID: #{patientId || '—'}
            </p>
          </div>
          <div className="profile-header__actions">
            <button
              type="button"
              className={`btn ${isEditing ? 'btn-ghost' : 'btn-primary'}`}
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? (
                <>
                  <X size={16} aria-hidden="true" />
                  Cancel
                </>
              ) : (
                <>
                  <Pencil size={16} aria-hidden="true" />
                  Edit Profile
                </>
              )}
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="firstName">First Name</label>
              <input
                id="firstName"
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </div>
            <div className="form-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                id="lastName"
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </div>
            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input
                id="phone"
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </div>
            <div className="form-group">
              <label htmlFor="dateOfBirth">Date of Birth</label>
              <input
                id="dateOfBirth"
                type="date"
                name="dateOfBirth"
                value={formData.dateOfBirth}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label htmlFor="address">Address</label>
              <textarea
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                disabled={!isEditing}
                rows={3}
              />
            </div>
          </div>

          {isEditing && (
            <div className="form-actions">
              <button type="submit" className="btn btn-success" disabled={saving}>
                <Save size={16} aria-hidden="true" />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </form>
      </div>

      {qrData?.qr_data && (
        <section className="card card--elevated" style={{ marginTop: '1.5rem' }}>
          <h2 className="section-title">
            <QrCode size={20} aria-hidden="true" style={{ verticalAlign: 'middle', marginRight: 8 }} />
            Clinic QR Code
          </h2>
          <p className="page-subtitle">Show this at reception for quick check-in.</p>
          <img
            src={qrData.qr_data}
            alt="Patient QR code"
            style={{ maxWidth: 200, display: 'block', margin: '1rem auto' }}
          />
        </section>
      )}
    </>
  )
}

export default PatientProfile
