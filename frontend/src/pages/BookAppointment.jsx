import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CalendarPlus,
  Stethoscope,
  Calendar,
  Clock,
  Video,
  MapPin,
  FileText,
  Loader2,
} from 'lucide-react'
import { getDoctors, getTimeslots, bookAppointment, getApiError } from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'

const BookAppointment = () => {
  const navigate = useNavigate()
  const [doctors, setDoctors] = useState([])
  const [selectedDoctor, setSelectedDoctor] = useState('')
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedTime, setSelectedTime] = useState('')
  const [timeslots, setTimeslots] = useState([])
  const [reason, setReason] = useState('')
  const [appointmentType, setAppointmentType] = useState('in-person')
  const [loading, setLoading] = useState(false)
  const [loadingDoctors, setLoadingDoctors] = useState(true)
  const [loadingTimeslots, setLoadingTimeslots] = useState(false)
  const [timeslotsError, setTimeslotsError] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    getDoctors()
      .then(setDoctors)
      .catch(() => setError('Failed to load doctors'))
      .finally(() => setLoadingDoctors(false))
  }, [])

  useEffect(() => {
    if (!selectedDoctor || !selectedDate) {
      setTimeslots([])
      setSelectedTime('')
      setTimeslotsError('')
      return
    }

    setSelectedTime('')
    setTimeslots([])
    setTimeslotsError('')
    setLoadingTimeslots(true)

    getTimeslots(selectedDoctor, selectedDate)
      .then((slots) => {
        setTimeslots(slots)
        if (!slots.length) {
          setTimeslotsError('No times available for this doctor on that date. Try another day.')
        }
      })
      .catch((err) => {
        setTimeslots([])
        setTimeslotsError(getApiError(err, 'Could not load available times.'))
      })
      .finally(() => setLoadingTimeslots(false))
  }, [selectedDoctor, selectedDate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    if (!selectedDoctor || !selectedDate || !selectedTime) {
      setError('Please fill in all required fields')
      setLoading(false)
      return
    }

    const doctor = doctors.find((d) => d.id === parseInt(selectedDoctor, 10))
    const appointmentData = {
      doctor_id: parseInt(selectedDoctor, 10),
      doctor_name: doctor?.name || '',
      appointment_date: selectedDate,
      time_slot: selectedTime,
      reason,
      type: appointmentType,
    }

    try {
      await bookAppointment(appointmentData)
      setSuccess('Appointment booked successfully!')
      setTimeout(() => navigate('/appointments'), 2000)
    } catch (err) {
      console.error('Error booking appointment:', err)
      setError(getApiError(err, 'Failed to book appointment. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  const today = new Date().toISOString().split('T')[0]

  if (loadingDoctors) {
    return <PageLoading message="Loading doctors..." />
  }

  return (
    <>
      <PageHeader
        eyebrow="Book a visit"
        icon={CalendarPlus}
        title="Book an appointment"
        subtitle="Choose a doctor, date, and time — in-person or virtual — at the campus clinic."
      />

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={handleSubmit} className="card card--elevated form-panel">
        <div className="form-group">
          <label htmlFor="doctor">
            <Stethoscope size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} aria-hidden="true" />
            Select Doctor *
          </label>
          <select
            id="doctor"
            value={selectedDoctor}
            onChange={(e) => setSelectedDoctor(e.target.value)}
            required
            disabled={loadingDoctors}
          >
            <option value="">-- Select a doctor --</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.name} - {doctor.specialization}
                {!doctor.available && ' (Not Available)'}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="date">
            <Calendar size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} aria-hidden="true" />
            Select Date *
          </label>
          <input
            id="date"
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            min={today}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="time">
            <Clock size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} aria-hidden="true" />
            Select Time *
          </label>
          <select
            id="time"
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
            required
            disabled={loadingTimeslots || !selectedDoctor || !selectedDate}
          >
            <option value="">-- Select a time --</option>
            {loadingTimeslots ? (
              <option disabled>Loading timeslots...</option>
            ) : (
              timeslots.map((time) => (
                <option key={time} value={time}>
                  {time}
                </option>
              ))
            )}
          </select>
          {timeslotsError && !loadingTimeslots && (
            <p className="page-subtitle" style={{ marginTop: '0.35rem', fontSize: '0.8125rem', color: 'var(--color-warning, #b45309)' }}>
              {timeslotsError}
            </p>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="type">Appointment Type *</label>
          <select
            id="type"
            value={appointmentType}
            onChange={(e) => setAppointmentType(e.target.value)}
          >
            <option value="in-person">In-Person Visit</option>
            <option value="online">Online Consultation</option>
          </select>
          <p className="page-subtitle" style={{ marginTop: '0.35rem', fontSize: '0.8125rem' }}>
            {appointmentType === 'online' ? (
              <>
                <Video size={13} style={{ verticalAlign: 'middle' }} aria-hidden="true" /> Virtual consultation
              </>
            ) : (
              <>
                <MapPin size={13} style={{ verticalAlign: 'middle' }} aria-hidden="true" /> Visit the clinic in person
              </>
            )}
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="reason">
            <FileText size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} aria-hidden="true" />
            Reason for Visit
          </label>
          <textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Please describe your symptoms or reason for visit..."
            rows={4}
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
          {loading ? (
            <>
              <Loader2 size={18} className="spin-icon" aria-hidden="true" />
              Booking...
            </>
          ) : (
            <>
              <CalendarPlus size={18} aria-hidden="true" />
              Book Appointment
            </>
          )}
        </button>
      </form>
    </>
  )
}

export default BookAppointment
