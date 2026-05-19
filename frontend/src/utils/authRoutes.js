export const PATIENT_ROLE = 'PATIENT'
export const STAFF_ROLES = ['DOCTOR', 'NURSE', 'RECEPTIONIST']
export const ADMIN_ROLE = 'ADMIN'

export function getDashboardPath(role) {
  if (role === PATIENT_ROLE) return '/dashboard'
  if (STAFF_ROLES.includes(role)) return '/staff/dashboard'
  if (role === ADMIN_ROLE) return '/admin/dashboard'
  return '/'
}

export function getLoginPath(role) {
  if (role === PATIENT_ROLE) return '/login'
  if (STAFF_ROLES.includes(role) || role === ADMIN_ROLE) return '/staff/login'
  return '/login'
}

export function roleLabel(role) {
  const labels = {
    PATIENT: 'Patient',
    DOCTOR: 'Doctor',
    NURSE: 'Nurse',
    ADMIN: 'Administrator',
    RECEPTIONIST: 'Reception',
  }
  return labels[role] || role
}
