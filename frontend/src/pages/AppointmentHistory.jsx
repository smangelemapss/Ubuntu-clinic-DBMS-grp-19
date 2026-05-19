import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Clock, Stethoscope, CalendarPlus, X } from 'lucide-react'
import { getUpcomingAppointments, getAppointmentHistory, cancelAppointment } from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'
import EmptyState from '../components/ui/EmptyState'
import Modal from '../components/ui/Modal'
import StatusBadge from '../components/ui/StatusBadge'

const AppointmentHistory = () => {
  const [upcoming, setUpcoming] = useState([])
  const [past, setPast] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('upcoming')
  const [cancellingId, setCancellingId] = useState(null)
  const [cancelReason, setCancelReason] = useState('')
  const [showCancelModal, setShowCancelModal] = useState(false)

  const loadAppointments = () => {
    Promise.all([getUpcomingAppointments(), getAppointmentHistory()])
      .then(([upcomingData, pastData]) => {
        setUpcoming(upcomingData)
        setPast(pastData)
      })
      .catch((err) => console.error('Error loading appointments:', err))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadAppointments()
  }, [])

  const handleCancelClick = (id) => {
    setCancellingId(id)
    setCancelReason('')
    setShowCancelModal(true)
  }

  const handleCancelConfirm = async () => {
    try {
      await cancelAppointment(cancellingId, cancelReason)
      setShowCancelModal(false)
      setCancellingId(null)
      setCancelReason('')
      loadAppointments()
    } catch (err) {
      console.error('Error cancelling appointment:', err)
    }
  }

  const appointments = activeTab === 'upcoming' ? upcoming : past

  if (loading) {
    return <PageLoading message="Loading appointments..." />
  }

  return (
    <>
      <PageHeader
        eyebrow="Scheduling"
        icon={Calendar}
        title="My appointments"
        subtitle="View upcoming visits, cancel when needed, and browse your past appointment history."
      />

      <div className="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          className={`tab${activeTab === 'upcoming' ? ' tab--active' : ''}`}
          onClick={() => setActiveTab('upcoming')}
        >
          <Calendar size={16} aria-hidden="true" />
          Upcoming ({upcoming.length})
        </button>
        <button
          type="button"
          role="tab"
          className={`tab${activeTab === 'past' ? ' tab--active' : ''}`}
          onClick={() => setActiveTab('past')}
        >
          <Clock size={16} aria-hidden="true" />
          Past ({past.length})
        </button>
      </div>

      {appointments.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title={activeTab === 'upcoming' ? 'No upcoming appointments' : 'No past appointments'}
          description={
            activeTab === 'upcoming'
              ? 'Book your next visit with a campus clinic doctor.'
              : 'Completed and past visits will show up here.'
          }
          action={
            activeTab === 'upcoming' ? (
              <Link to="/book-appointment" className="btn btn-primary">
                <CalendarPlus size={18} aria-hidden="true" />
                Book an Appointment
              </Link>
            ) : null
          }
        />
      ) : (
        <div className="list-stack">
          {appointments.map((apt) => (
            <article key={apt.id} className="list-card">
              <div className="list-card__header">
                <div>
                  <h3 className="list-card__title">{apt.appointment_date}</h3>
                  <p className="list-card__meta">
                    <Clock size={14} aria-hidden="true" />
                    {apt.time_slot}
                  </p>
                </div>
                <StatusBadge status={apt.status} />
              </div>
              <div className="list-card__body">
                <p className="list-card__meta">
                  <Stethoscope size={14} aria-hidden="true" />
                  <strong>Doctor:</strong> {apt.doctor_name}
                </p>
                <p style={{ marginTop: '0.35rem' }}>
                  <strong>Type:</strong> {apt.type}
                </p>
              </div>
              {activeTab === 'upcoming' && apt.status !== 'cancelled' && (
                <div className="list-card__actions">
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => handleCancelClick(apt.id)}
                  >
                    <X size={15} aria-hidden="true" />
                    Cancel Appointment
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}

      {showCancelModal && (
        <Modal
          title="Cancel Appointment"
          onClose={() => setShowCancelModal(false)}
          footer={
            <>
              <button type="button" className="btn btn-ghost" onClick={() => setShowCancelModal(false)}>
                No, Keep It
              </button>
              <button type="button" className="btn btn-danger" onClick={handleCancelConfirm}>
                Yes, Cancel
              </button>
            </>
          }
        >
          <p style={{ marginBottom: '1rem', color: 'var(--color-text-muted)' }}>
            Are you sure you want to cancel this appointment?
          </p>
          <div className="form-group">
            <label htmlFor="cancel-reason">Reason (optional)</label>
            <textarea
              id="cancel-reason"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="Please provide a reason for cancellation..."
              rows={4}
            />
          </div>
        </Modal>
      )}
    </>
  )
}

export default AppointmentHistory
