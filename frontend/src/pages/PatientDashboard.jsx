import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Calendar,
  History,
  FlaskConical,
  CalendarX,
  CalendarPlus,
  FileText,
  Phone,
  LayoutDashboard,
} from 'lucide-react'
import { getPatientDashboard, getPendingResults } from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'
import StatCard from '../components/ui/StatCard'
import EmptyState from '../components/ui/EmptyState'

const PatientDashboard = () => {
  const [dashboard, setDashboard] = useState({
    upcomingCount: 0,
    pastVisitsCount: 0,
    pendingResultsCount: 0,
    cancelledCount: 0,
  })
  const [pendingResults, setPendingResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getPatientDashboard(), getPendingResults()])
      .then(([dash, pending]) => {
        setDashboard(dash)
        setPendingResults(Array.isArray(pending) ? pending : [])
      })
      .catch((err) => console.error('Error loading dashboard:', err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <PageLoading message="Loading dashboard..." />
  }

  return (
    <div>
      <PageHeader
        eyebrow="Patient portal"
        icon={LayoutDashboard}
        title="Your health dashboard"
        subtitle="Overview of appointments, visits, and pending results — everything in one place."
      />

      <div className="stats-grid">
        <StatCard
          icon={Calendar}
          value={dashboard.upcomingCount}
          label="Upcoming Appointments"
          tone="teal"
        />
        <StatCard
          icon={History}
          value={dashboard.pastVisitsCount}
          label="Past Visits"
          tone="blue"
        />
        <StatCard
          icon={FlaskConical}
          value={dashboard.pendingResultsCount}
          label="Pending Results"
          tone="amber"
        />
        <StatCard
          icon={CalendarX}
          value={dashboard.cancelledCount}
          label="Cancelled Appointments"
          tone="rose"
        />
      </div>

      {pendingResults.length > 0 && (
        <section className="card card--elevated" style={{ marginBottom: '1.5rem' }}>
          <h2 className="section-title">Pending results</h2>
          <ul className="staff-notifications">
            {pendingResults.map((item) => (
              <li key={item.id} className="staff-notif">
                <div>
                  <strong>{item.test || 'Lab result'}</strong>
                  <p>
                    {item.date} · {item.status || 'Pending'}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="card card--elevated">
        <h2 className="section-title">Quick Actions</h2>
        <p className="page-subtitle" style={{ marginBottom: '1rem' }}>
          Jump to the tasks you use most often.
        </p>
        <div className="action-tiles">
          <Link to="/book-appointment" className="action-tile">
            <div className="action-tile__icon action-tile__icon--primary">
              <CalendarPlus size={22} />
            </div>
            <div>
              <div className="action-tile__label">Book Appointment</div>
              <div className="action-tile__hint">Schedule your next visit</div>
            </div>
          </Link>
          <Link to="/medical-history" className="action-tile">
            <div className="action-tile__icon action-tile__icon--secondary">
              <FileText size={22} />
            </div>
            <div>
              <div className="action-tile__label">Medical History</div>
              <div className="action-tile__hint">Records & diagnoses</div>
            </div>
          </Link>
          <Link to="/emergency-contacts" className="action-tile">
            <div className="action-tile__icon action-tile__icon--danger">
              <Phone size={22} />
            </div>
            <div>
              <div className="action-tile__label">Emergency Contacts</div>
              <div className="action-tile__hint">Manage trusted contacts</div>
            </div>
          </Link>
        </div>
      </section>

      {pendingResults.length === 0 && dashboard.pendingResultsCount > 0 && (
        <EmptyState
          title="Pending results on file"
          description="You have pending results — details will appear when loaded from the server."
        />
      )}
    </div>
  )
}

export default PatientDashboard
