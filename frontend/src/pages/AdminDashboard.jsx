import { useEffect, useState } from 'react'
import { Users, Stethoscope, Calendar, Percent, Building2, ScrollText, Shield } from 'lucide-react'
import {
  getAdminSummary,
  getAdminDepartments,
  getAdminUsers,
  getAdminAuditLog,
  createAdminDepartment,
  updateAdminUser,
  getApiError,
} from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'
import StatCard from '../components/ui/StatCard'
import './AdminDashboard.css'

const ROLES = ['PATIENT', 'DOCTOR', 'NURSE', 'RECEPTIONIST', 'ADMIN']

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null)
  const [departments, setDepartments] = useState([])
  const [users, setUsers] = useState([])
  const [auditLog, setAuditLog] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [newDeptName, setNewDeptName] = useState('')
  const [tab, setTab] = useState('overview')

  const loadAll = () => {
    setLoading(true)
    Promise.all([
      getAdminSummary(),
      getAdminDepartments(),
      getAdminUsers(),
      getAdminAuditLog({ per_page: 25 }),
    ])
      .then(([sum, depts, userList, audit]) => {
        setSummary(sum)
        setDepartments(Array.isArray(depts) ? depts : [])
        setUsers(userList?.results || [])
        setAuditLog(audit?.results || [])
      })
      .catch((err) => setError(getApiError(err, 'Could not load admin data.')))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadAll()
  }, [])

  const handleCreateDept = async (e) => {
    e.preventDefault()
    if (!newDeptName.trim()) return
    setError('')
    setSuccess('')
    try {
      await createAdminDepartment(newDeptName.trim())
      setNewDeptName('')
      setSuccess('Department created.')
      loadAll()
    } catch (err) {
      setError(getApiError(err, 'Failed to create department.'))
    }
  }

  const handleRoleChange = async (userId, role) => {
    setError('')
    setSuccess('')
    try {
      await updateAdminUser(userId, { role })
      setSuccess(`User role updated to ${role}.`)
      loadAll()
    } catch (err) {
      setError(getApiError(err, 'Failed to update user.'))
    }
  }

  if (loading) {
    return <PageLoading message="Loading admin console..." />
  }

  return (
    <div>
      <PageHeader
        eyebrow="Administration"
        icon={Shield}
        title="Admin console"
        subtitle="Manage departments, staff accounts, clinic metrics, and system audit logs."
      />

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="admin-tabs">
        {['overview', 'departments', 'users', 'audit'].map((t) => (
          <button
            key={t}
            type="button"
            className={`admin-tab${tab === t ? ' admin-tab--active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'overview' && summary && (
        <div className="stats-grid admin-stat-grid">
          <StatCard icon={Users} value={summary.total_patients ?? 0} label="Registered patients" tone="teal" />
          <StatCard icon={Stethoscope} value={summary.total_doctors ?? 0} label="Doctors on staff" tone="sky" />
          <StatCard icon={Calendar} value={summary.appointments_today ?? 0} label="Appointments today" tone="amber" />
          <StatCard icon={Percent} value={`${summary.cancellation_rate ?? 0}%`} label="Cancellation rate" tone="slate" />
        </div>
      )}

      {tab === 'departments' && (
        <section className="admin-panel">
          <h2>
            <Building2 size={20} aria-hidden="true" /> Departments
          </h2>
          <form className="admin-inline-form" onSubmit={handleCreateDept}>
            <input
              type="text"
              placeholder="New department name"
              value={newDeptName}
              onChange={(e) => setNewDeptName(e.target.value)}
            />
            <button type="submit" className="btn btn-primary">
              Add department
            </button>
          </form>
          {departments.length === 0 ? (
            <p className="admin-empty">No departments found.</p>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Head doctor</th>
                  <th>Staff</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((d) => (
                  <tr key={d.id}>
                    <td>{d.name}</td>
                    <td>{d.head_doctor || '—'}</td>
                    <td>{d.staff_count ?? 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {tab === 'users' && (
        <section className="admin-panel">
          <h2>User accounts</h2>
          {users.length === 0 ? (
            <p className="admin-empty">No users found.</p>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Change role</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td>{u.role}</td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="admin-select"
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>{u.is_active ? 'Active' : 'Disabled'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {tab === 'audit' && (
        <section className="admin-panel">
          <h2>
            <ScrollText size={20} aria-hidden="true" /> Audit log
          </h2>
          {auditLog.length === 0 ? (
            <p className="admin-empty">No audit entries yet. Perform login, booking, or admin actions.</p>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Action</th>
                  <th>Time</th>
                  <th>Detail</th>
                </tr>
              </thead>
              <tbody>
                {auditLog.map((row) => (
                  <tr key={row.id}>
                    <td>{row.user}</td>
                    <td>{row.action}</td>
                    <td>{row.timestamp ? new Date(row.timestamp).toLocaleString() : '—'}</td>
                    <td>{row.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  )
}
