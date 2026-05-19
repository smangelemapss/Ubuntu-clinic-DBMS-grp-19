// frontend/src/components/doctor/BookingForm.jsx
import { useState } from 'react';
import { searchPatient, getAvailableTimeslots, createAppointment, getDoctors } from '../../services/api';

const BookingForm = ({ doctorId, doctorName, onBookingSuccess }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [reason, setReason] = useState('');
  const [appointmentType, setAppointmentType] = useState('in-person');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError('');
    try {
      const results = await searchPatient(searchQuery);
      setSearchResults(results);
    } catch (err) {
      setError('Failed to search patients');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPatient = (patient) => {
    setSelectedPatient(patient);
    setStep(2);
  };

  const handleDateChange = async (date) => {
    setSelectedDate(date);
    setSelectedTime('');
    setError('');
    setLoading(true);
    try {
      const slots = await getAvailableTimeslots(doctorId, date);
      setAvailableSlots(slots.filter(slot => slot.is_available));
    } catch (err) {
      if (err.response?.status === 409) {
        setError('This slot is no longer available');
      } else {
        setError('Failed to load available timeslots');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDate || !selectedTime || !reason) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const appointmentData = {
        doctor_id: doctorId,
        date: selectedDate,
        time_slot: selectedTime,
        reason: reason,
        type: appointmentType,
        patient_id: selectedPatient.id
      };

      const result = await createAppointment(appointmentData);
      setSuccess(`Appointment booked successfully for ${selectedPatient.first_name} ${selectedPatient.last_name}`);
      setStep(3);
      if (onBookingSuccess) onBookingSuccess(result);
    } catch (err) {
      if (err.response?.status === 409) {
        setError('This time slot is no longer available. Please select another time.');
      } else {
        setError('Failed to book appointment. Please try again.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setStep(1);
    setSearchQuery('');
    setSearchResults([]);
    setSelectedPatient(null);
    setSelectedDate('');
    setSelectedTime('');
    setAvailableSlots([]);
    setReason('');
    setAppointmentType('in-person');
    setError('');
    setSuccess('');
  };

  if (step === 3 && success) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Appointment Booked!</h3>
          <p className="text-gray-600 mb-6">{success}</p>
          <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
            <p className="text-sm text-gray-600"><strong>Patient:</strong> {selectedPatient?.first_name} {selectedPatient?.last_name}</p>
            <p className="text-sm text-gray-600"><strong>Date:</strong> {selectedDate}</p>
            <p className="text-sm text-gray-600"><strong>Time:</strong> {selectedTime}</p>
            <p className="text-sm text-gray-600"><strong>Type:</strong> {appointmentType === 'in-person' ? 'In-person' : 'Virtual'}</p>
            <p className="text-sm text-gray-600"><strong>Reason:</strong> {reason}</p>
          </div>
          <button
            onClick={resetForm}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            Book Another Appointment
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Book Appointment</h2>

      {/* Step Indicator */}
      <div className="flex items-center justify-between mb-8">
        <div className={`flex-1 text-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full mx-auto flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
            1
          </div>
          <span className="text-xs mt-1 block">Find Patient</span>
        </div>
        <div className={`flex-1 h-0.5 mx-2 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`} />
        <div className={`flex-1 text-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full mx-auto flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
            2
          </div>
          <span className="text-xs mt-1 block">Select Slot</span>
        </div>
        <div className={`flex-1 h-0.5 mx-2 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`} />
        <div className={`flex-1 text-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full mx-auto flex items-center justify-center ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
            3
          </div>
          <span className="text-xs mt-1 block">Confirm</span>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Step 1: Search Patient */}
      {step === 1 && (
        <div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Patient (Name or Student Number)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter name or student number..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={handleSearch}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium px-4 py-2 rounded-lg transition-colors"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-4">
              <h3 className="font-medium text-gray-700 mb-2">Search Results</h3>
              <div className="space-y-2">
                {searchResults.map(patient => (
                  <div
                    key={patient.id}
                    onClick={() => handleSelectPatient(patient)}
                    className="p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-800">
                          {patient.first_name} {patient.last_name}
                        </p>
                        <p className="text-sm text-gray-500">Student: {patient.student_number}</p>
                      </div>
                      <button className="text-blue-600 hover:text-blue-700">Select →</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {searchQuery && searchResults.length === 0 && !loading && (
            <div className="mt-4 text-center py-8 text-gray-500">
              No patients found. Check the name or student number.
            </div>
          )}
        </div>
      )}

      {/* Step 2: Select Date and Time */}
      {step === 2 && (
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Selected Patient
            </label>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-800">{selectedPatient?.first_name} {selectedPatient?.last_name}</p>
              <p className="text-sm text-gray-500">Student: {selectedPatient?.student_number}</p>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Appointment Date
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => handleDateChange(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {availableSlots.length > 0 && selectedDate && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Time Slots
              </label>
              <div className="grid grid-cols-4 gap-2">
                {availableSlots.map(slot => (
                  <button
                    key={slot.id}
                    type="button"
                    onClick={() => setSelectedTime(slot.time)}
                    className={`p-2 rounded-lg text-center transition-colors ${
                      selectedTime === slot.time
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                    }`}
                  >
                    {slot.time}
                  </button>
                ))}
              </div>
            </div>
          )}

          {selectedDate && availableSlots.length === 0 && !loading && (
            <div className="mb-4 text-center py-4 text-gray-500">
              No available slots for this date
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Appointment Type
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  value="in-person"
                  checked={appointmentType === 'in-person'}
                  onChange={(e) => setAppointmentType(e.target.value)}
                  className="text-blue-600"
                />
                <span>In-person</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  value="virtual"
                  checked={appointmentType === 'virtual'}
                  onChange={(e) => setAppointmentType(e.target.value)}
                  className="text-blue-600"
                />
                <span>Virtual</span>
              </label>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Visit
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows="3"
              placeholder="Describe symptoms or reason for appointment..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => {
                setStep(1);
                setSelectedDate('');
                setSelectedTime('');
              }}
              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={loading || !selectedDate || !selectedTime}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {loading ? 'Booking...' : 'Book Appointment'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default BookingForm;