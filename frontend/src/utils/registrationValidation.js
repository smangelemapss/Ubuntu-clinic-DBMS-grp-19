const STUDENT_NUMBER_RE = /^\d{8}$/
const NWU_EMAIL_RE = /^(\d{8})@mynwu\.ac\.za$/i
const PASSWORD_RE = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/

export const NWU_EMAIL_DOMAIN = '@mynwu.ac.za'

export function expectedNwuEmail(studentNumber) {
  return `${studentNumber.trim()}${NWU_EMAIL_DOMAIN}`
}

export function validateStudentNumber(studentNumber) {
  const value = studentNumber.trim()
  if (!value) return 'Enter your 8-digit NWU student number (e.g. 48277444).'
  if (!STUDENT_NUMBER_RE.test(value)) {
    return 'Student number must be exactly 8 digits (e.g. 48277444).'
  }
  return null
}

export function validateNwuEmail(email, studentNumber) {
  const normalized = email.trim().toLowerCase()
  const student = studentNumber.trim()
  if (!normalized) return 'Enter your NWU email (e.g. 48277444@mynwu.ac.za).'
  const match = NWU_EMAIL_RE.exec(normalized)
  if (!match) return `Email must be your student number followed by ${NWU_EMAIL_DOMAIN}`
  if (match[1] !== student) {
    return `Email must match your student number (e.g. ${expectedNwuEmail(student)})`
  }
  return null
}

export function validatePassword(password) {
  if (!password) return 'Password is required.'
  if (password.length < 8) return 'Password must be at least 8 characters.'
  if (!PASSWORD_RE.test(password)) {
    return 'Password must include at least one letter and one number.'
  }
  return null
}

export function validateUsername(username) {
  let value = username.trim().toLowerCase()
  if (value.includes(' ')) {
    value = value.split(/\s+/).join('.')
  }
  if (!value) return { error: 'Username is required.', username: value }
  if (!value.includes('.')) {
    return {
      error: 'Use a username like firstname.lastname (e.g. karabo.mabena).',
      username: value,
    }
  }
  return { error: null, username: value }
}
