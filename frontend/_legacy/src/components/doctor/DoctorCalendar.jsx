// frontend/src/components/doctor/DoctorCalendar.jsx
import { useState, useCallback } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

const DoctorCalendar = ({ appointments, doctorId, onRefresh }) => {
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Transform appointments to calendar events
  const events = appointments.map(appt => {
    const [year, month, day] = appt.date.split('-');
    const [hour, minute] = appt.time.split(':');
    const startDate = new Date(year, month - 1, day, parseInt(hour), parseInt(minute));
    const endDate = new Date(startDate.getTime() + 30 * 60000); // 30 min appointments

    return {
      id: appt.id,
      title: `${appt.doctor} - ${appt.type === 'virtual' ? 'Virtual' : 'In-person'}`,
      start: startDate,
      end: endDate,
      patientName: appt.patient_name,
      status: appt.status,
      type: appt.type,
      department: appt.department
    };
  });

  const handleSelectEvent = useCallback((event) => {
    setSelectedEvent(event);
  }, []);

  const closeModal = () => {
    setSelectedEvent(null);
  };

  const eventStyleGetter = (event) => {
    let backgroundColor = '#3b82f6'; // blue
    if (event.status === 'completed') backgroundColor = '#10b981'; // green
    if (event.status === 'cancelled') backgroundColor = '#ef4444'; // red
    
    return {
      style: {
        backgroundColor,
        borderRadius: '6px',
        border: 'none',
        color: 'white',
        fontSize: '12px',
        padding: '2px 6px'
      }
    };
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Appointment Calendar</h2>
        <button
          onClick={onRefresh}
          className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        onSelectEvent={handleSelectEvent}
        eventPropGetter={eventStyleGetter}
        views={['month', 'week', 'day']}
        defaultView="week"
        min={new Date(2024, 0, 1, 8, 0)}
        max={new Date(2024, 0, 1, 17, 0)}
      />

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="border-b border-gray-200 p-4 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-800">Appointment Details</h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-500">Time:</span>
                <span className="text-gray-800">
                  {moment(selectedEvent.start).format('MMMM D, YYYY h:mm A')} - {moment(selectedEvent.end).format('h:mm A')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Doctor:</span>
                <span className="text-gray-800">{selectedEvent.title.split(' - ')[0]}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Type:</span>
                <span className="text-gray-800">{selectedEvent.type === 'virtual' ? 'Virtual' : 'In-person'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Status:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  selectedEvent.status === 'upcoming' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                }`}>
                  {selectedEvent.status || 'Upcoming'}
                </span>
              </div>
            </div>
            <div className="border-t border-gray-200 p-4">
              <button
                onClick={closeModal}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorCalendar;