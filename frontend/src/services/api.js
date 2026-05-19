import axiosInstance from '../api/axios/Instance'
import {
  validateNwuEmail,
  validatePassword,
  validateStudentNumber,
  validateUsername,
} from '../utils/registrationValidation'

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

/** Extract user-facing message from backend error responses */
export function getApiError(error, fallback = 'Something went wrong. Please try again.') {
  if (!error?.response) {
    return 'Cannot reach the server. Start the backend: cd backend && python app.py'
  }
  const data = error.response.data
  return data?.error || data?.message || fallback
}

function normalizeUpcoming(rows) {
  return (rows || []).map((apt) => ({
    id: apt.id,
    appointment_date: apt.appointment_date || apt.date,
    time_slot: apt.time_slot || apt.time,
    doctor_name: apt.doctor_name || apt.doctor,
    type: apt.type || apt.booking_type || 'in-person',
    status: (apt.status === 'upcoming' ? 'confirmed' : (apt.status || 'confirmed')).toLowerCase(),
  }))
}

function normalizeHistory(rows) {
  return (rows || []).map((apt) => ({
    id: apt.id,
    appointment_date: apt.appointment_date || apt.date,
    time_slot: apt.time_slot || apt.time,
    doctor_name: apt.doctor_name || apt.doctor,
    department: apt.department,
    diagnosis: apt.diagnosis,
    type: apt.type,
    status: (apt.status || 'completed').toLowerCase(),
  }))
}

function formatSlotTime(value) {
  if (value == null) return ''
  const text = String(value).trim()
  if (!text) return ''
  const timePart = text.includes('T') ? text.split('T')[1] : text
  if (/^\d{1,2}:\d{2}/.test(timePart)) return timePart.slice(0, 5)
  return text.slice(0, 5)
}

function normalizeTimeslots(rows) {
  const list = Array.isArray(rows) ? rows : rows?.data
  if (!list?.length) return []
  if (typeof list[0] === 'string') return list.map(formatSlotTime).filter(Boolean)
  return list
    .filter((s) => s.is_available !== false && s.is_available !== 0)
    .map((s) => formatSlotTime(s.time ?? s.start_time))
    .filter(Boolean)
}

export const getHealth = async () => {
  const response = await axiosInstance.get('/api/v1/health/')
  return response.data
}

export const getPatientDashboard = async () => {
  if (USE_MOCK) {
    return { upcomingCount: 0, pastVisitsCount: 0, pendingResultsCount: 0, cancelledCount: 0 }
  }
  const response = await axiosInstance.get('/api/v1/patient/dashboard/')
  return response.data
}

export const getPatientProfile = async () => {
  const response = await axiosInstance.get('/api/v1/patient/profile/')
  return response.data
}

export const getMedicalRecords = async () => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/medical/records/')
  return response.data
}

export const getMedicalRecordById = async (id) => {
  if (USE_MOCK) return null
  const response = await axiosInstance.get(`/api/v1/medical/records/${id}/`)
  return response.data
}

export const getEmergencyContacts = async () => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/emergency-contacts/')
  return response.data
}

export const createEmergencyContact = async (data) => {
  const response = await axiosInstance.post('/api/v1/emergency-contacts/', data)
  return response.data
}

export const updateEmergencyContact = async (id, data) => {
  const response = await axiosInstance.patch(`/api/v1/emergency-contacts/${id}/`, data)
  return response.data
}

export const deleteEmergencyContact = async (id) => {
  const response = await axiosInstance.delete(`/api/v1/emergency-contacts/${id}/`)
  return response.data
}

export const getUpcomingAppointments = async () => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/appointments/upcoming/')
  return normalizeUpcoming(response.data)
}

export const getAppointmentHistory = async () => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/appointments/history/')
  return normalizeHistory(response.data)
}

export const bookAppointment = async (data) => {
  const payload = {
    doctor_id: data.doctor_id,
    date: data.date || data.appointment_date,
    time_slot: data.time_slot,
    reason: (data.reason || '').trim() || 'General consultation',
    type: data.type === 'online' ? 'online' : data.type || 'in-person',
  }
  const response = await axiosInstance.post('/api/v1/appointments/book/', payload)
  return response.data
}

export const cancelAppointment = async (id, reason) => {
  const response = await axiosInstance.patch(`/api/v1/appointments/${id}/cancel/`, {
    cancellation_reason: reason || '',
  })
  return response.data
}

export const getDoctors = async () => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/doctors/')
  return response.data
}

export const getTimeslots = async (doctorId, date) => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/timeslots/', {
    params: { doctor_id: doctorId, date },
  })
  return normalizeTimeslots(response.data)
}

export const registerPatient = async (data) => {
  const { error: usernameError, username } = validateUsername(data.username || '')
  if (usernameError) {
    throw Object.assign(new Error(usernameError), { code: 'VALIDATION_ERROR' })
  }

  const studentError = validateStudentNumber(data.student_number || '')
  if (studentError) {
    throw Object.assign(new Error(studentError), { code: 'VALIDATION_ERROR' })
  }

  const email = (data.email || '').trim().toLowerCase()
  const emailError = validateNwuEmail(email, data.student_number || '')
  if (emailError) {
    throw Object.assign(new Error(emailError), { code: 'VALIDATION_ERROR' })
  }

  const passwordError = validatePassword(data.password || '')
  if (passwordError) {
    throw Object.assign(new Error(passwordError), { code: 'VALIDATION_ERROR' })
  }

  const response = await axiosInstance.post('/api/v1/auth/register/', {
    username,
    student_number: String(data.student_number).trim(),
    email,
    password: data.password,
  })
  return response.data
}

export const getNotifications = async () => {
  const response = await axiosInstance.get('/api/v1/notifications/')
  return response.data
}

export const markNotificationRead = async (id) => {
  const response = await axiosInstance.patch(`/api/v1/notifications/${id}/read/`)
  return response.data
}

export const getAdminSummary = async () => {
  const response = await axiosInstance.get('/api/v1/admin/reports/summary/')
  return response.data
}

export const getAdminDepartments = async () => {
  const response = await axiosInstance.get('/api/v1/admin/departments/')
  return response.data
}

export const getAdminUsers = async () => {
  const response = await axiosInstance.get('/api/v1/admin/users/', {
    params: { per_page: 50 },
  })
  return response.data
}

export const updatePatientProfile = async (data) => {
  const response = await axiosInstance.patch('/api/v1/patient/profile/', {
    first_name: data.firstName || data.first_name,
    last_name: data.lastName || data.last_name,
    email: data.email,
    phone: data.phone,
    date_of_birth: data.dateOfBirth || data.date_of_birth,
    address: data.address,
  })
  return response.data
}

export const getPatientQrCode = async () => {
  const response = await axiosInstance.get('/api/v1/patient/qr-code/')
  return response.data
}

export const getPendingResults = async () => {
  if (USE_MOCK) return []
  const response = await axiosInstance.get('/api/v1/appointments/pending-results/')
  return response.data
}

export const markAllNotificationsRead = async () => {
  const response = await axiosInstance.patch('/api/v1/notifications/read-all/')
  return response.data
}

export const queueCheckIn = async (appointmentId) => {
  const response = await axiosInstance.post('/api/v1/queue/check-in/', {
    appointment_id: appointmentId,
  })
  return response.data
}

export const getQueueStatus = async (appointmentId) => {
  const response = await axiosInstance.get(`/api/v1/queue/${appointmentId}/`)
  return response.data
}

export const getAdminAuditLog = async (params = {}) => {
  const response = await axiosInstance.get('/api/v1/admin/audit-log/', { params })
  return response.data
}

export const createAdminDepartment = async (name, headDoctorId = null) => {
  const response = await axiosInstance.post('/api/v1/admin/departments/', {
    name,
    head_doctor_id: headDoctorId,
  })
  return response.data
}

export const updateAdminDepartment = async (id, data) => {
  const response = await axiosInstance.patch(`/api/v1/admin/departments/${id}/`, data)
  return response.data
}

export const updateAdminUser = async (id, data) => {
  const response = await axiosInstance.patch(`/api/v1/admin/users/${id}/`, data)
  return response.data
}
