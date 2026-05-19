import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

import { useAuth } from './context/AuthContext'

import Layout from './components/Layout'
import StaffLayout from './components/StaffLayout'
import AdminLayout from './components/AdminLayout'
import ProtectedRoute from './components/ProtectedRoute'
import PageLoading from './components/ui/PageLoading'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

import {
  PATIENT_ROLE,
  STAFF_ROLES,
  ADMIN_ROLE,
  getDashboardPath,
} from './utils/authRoutes'

const PatientDashboard = lazy(() => import('./pages/PatientDashboard'))
const MedicalHistory = lazy(() => import('./pages/MedicalHistory'))
const EmergencyContacts = lazy(() => import('./pages/EmergencyContacts'))
const AppointmentHistory = lazy(() => import('./pages/AppointmentHistory'))
const BookAppointment = lazy(() => import('./pages/BookAppointment'))
const PatientProfile = lazy(() => import('./pages/PatientProfile'))
const StaffDashboard = lazy(() => import('./pages/StaffDashboard'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))

function AuthRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={getDashboardPath(user.role)} replace />
}

function LazyPage({ children }) {
  return <Suspense fallback={<PageLoading />}>{children}</Suspense>
}

function App() {
  const { user } = useAuth()

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />

      <Route
        path="/login"
        element={user ? <AuthRedirect /> : <LoginPage portal="patient" />}
      />
      <Route
        path="/staff/login"
        element={user ? <AuthRedirect /> : <LoginPage portal="staff" />}
      />
      <Route
        path="/register"
        element={user ? <AuthRedirect /> : <RegisterPage />}
      />

      <Route element={<ProtectedRoute roles={[PATIENT_ROLE]} />}>
        <Route element={<Layout />}>
          <Route
            path="/dashboard"
            element={
              <LazyPage>
                <PatientDashboard />
              </LazyPage>
            }
          />
          <Route
            path="/medical-history"
            element={
              <LazyPage>
                <MedicalHistory />
              </LazyPage>
            }
          />
          <Route
            path="/emergency-contacts"
            element={
              <LazyPage>
                <EmergencyContacts />
              </LazyPage>
            }
          />
          <Route
            path="/appointments"
            element={
              <LazyPage>
                <AppointmentHistory />
              </LazyPage>
            }
          />
          <Route
            path="/book-appointment"
            element={
              <LazyPage>
                <BookAppointment />
              </LazyPage>
            }
          />
          <Route
            path="/profile"
            element={
              <LazyPage>
                <PatientProfile />
              </LazyPage>
            }
          />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={STAFF_ROLES} />}>
        <Route element={<StaffLayout />}>
          <Route
            path="/staff/dashboard"
            element={
              <LazyPage>
                <StaffDashboard />
              </LazyPage>
            }
          />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={[ADMIN_ROLE]} />}>
        <Route element={<AdminLayout />}>
          <Route
            path="/admin/dashboard"
            element={
              <LazyPage>
                <AdminDashboard />
              </LazyPage>
            }
          />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
