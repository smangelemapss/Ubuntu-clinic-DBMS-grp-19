import { useEffect, useState } from 'react'
import { Bell, Stethoscope, Users } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import {
  getNotifications,
  markNotificationRead,
  queueCheckIn,
  getQueueStatus,
  getApiError,
} from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'
import EmptyState from '../components/ui/EmptyState'
import { roleLabel } from '../utils/authRoutes'
import './StaffDashboard.css'

export default function StaffDashboard() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [appointmentId, setAppointmentId] = useState('')
  const [queueInfo, setQueueInfo] = useState(null)
  const [queueBusy, setQueueBusy] = useState(false)

  useEffect(() => {
    getNotifications()
      .then((rows) => setNotifications(Array.isArray(rows) ? rows : []))
      .catch((err) => setError(getApiError(err, 'Could not load notifications.')))
      .finally(() => setLoading(false))
  }, [])

  const handleMarkRead = async (id) => {
    try {
      await markNotificationRead(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      )
    } catch {
      /* ignore */
    }
  }

  const handleCheckIn = async (e) => {
    e.preventDefault()
    const id = parseInt(appointmentId, 10)
    if (!id) return
    setQueueBusy(true)
    setError('')
    setQueueInfo(null)
    try {
      await queueCheckIn(id)
      const status = await getQueueStatus(id)
      setQueueInfo(status)
    } catch (err) {
      setError(getApiError(err, 'Check-in failed.'))
    } finally {
      setQueueBusy(false)
    }
  }

  const handleLookupQueue = async () => {
    const id = parseInt(appointmentId, 10)
    if (!id) return
    setQueueBusy(true)
    setError('')
    try {
      const status = await getQueueStatus(id)
      setQueueInfo(status)
    } catch (err) {
      setError(getApiError(err, 'Queue entry not found.'))
    } finally {
      setQueueBusy(false)
    }
  }

  if (loading) {
    return <PageLoading message="Loading staff dashboard..." />
  }

  const unread = notifications.filter((n) => !n.read).length

  return (
    <div>
      <PageHeader
        eyebrow="Staff portal"
        icon={Stethoscope}
        title={`${roleLabel(user?.role)} workspace`}
        subtitle="Notifications, patient check-in, and queue status for campus clinic operations."
      />

      {error && <div className="alert alert-error">{error}</div>}

      <section className="staff-welcome">
        <Stethoscope size={28} aria-hidden="true" />
        <div>
          <h2>Welcome, {user?.username}</h2>
          <p>
            Reception and clinical staff use this portal for notifications and queue check-in.
          </p>
        </div>
      </section>

      <section className="staff-section card card--elevated">
        <h3 className="staff-section__title">
          <Users size={20} aria-hidden="true" />
          Queue check-in
        </h3>
        <form className="staff-queue-form" onSubmit={handleCheckIn}>
          <label htmlFor="apptId">Appointment ID</label>
          <div className="staff-queue-form__row">
            <input
              id="apptId"
              type="number"
              min="1"
              value={appointmentId}
              onChange={(e) => setAppointmentId(e.target.value)}
              placeholder="e.g. 1"
            />
            <button type="submit" className="btn btn-primary" disabled={queueBusy}>
              Check in
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              disabled={queueBusy}
              onClick={handleLookupQueue}
            >
              Lookup
            </button>
          </div>
        </form>
        {queueInfo && (
          <div className="staff-queue-result">
            <strong>Queue status</strong>
            <pre>{JSON.stringify(queueInfo, null, 2)}</pre>
          </div>
        )}
      </section>

      <section className="staff-section">
        <h3 className="staff-section__title">
          <Bell size={20} aria-hidden="true" />
          Notifications
          {unread > 0 && <span className="staff-badge">{unread} new</span>}
        </h3>

        {notifications.length === 0 ? (
          <EmptyState
            title="No notifications"
            description="You are all caught up. New alerts will appear here."
          />
        ) : (
          <ul className="staff-notifications">
            {notifications.map((n) => (
              <li key={n.id} className={`staff-notif${n.read ? ' staff-notif--read' : ''}`}>
                <div>
                  <strong>{n.title || 'Notification'}</strong>
                  {n.text && <p>{n.text}</p>}
                </div>
                {!n.read && (
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleMarkRead(n.id)}
                  >
                    Mark read
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
