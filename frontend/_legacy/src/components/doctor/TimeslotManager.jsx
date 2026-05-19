// frontend/src/components/doctor/TimeslotManager.jsx
import { useState, useEffect } from 'react';
import { getAvailableTimeslots, addTimeslot, removeTimeslot } from '../../services/api';

const TimeslotManager = ({ doctorId, appointments, onRefresh }) => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [timeslots, setTimeslots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [newTime, setNewTime] = useState('');
  const [error, setError] = useState(null);

  const timeOptions = [];
  for (let hour = 8; hour <= 16; hour++) {
    for (let minute of [0, 30]) {
      if (hour === 16 && minute === 30) continue;
      const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      timeOptions.push(time);
    }
  }

  useEffect(() => {
    loadTimeslots();
  }, [selectedDate, doctorId]);

  const loadTimeslots = async () => {
    setLoading(true);
    setError(null);
    try {
      const slots = await getAvailableTimeslots(doctorId, selectedDate);
      setTimeslots(slots);
    } catch (err) {
      console.error('Error loading timeslots:', err);
      setError('Failed to load timeslots');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTimeslot = async () => {
    if (!newTime) return;
    setAdding(true);
    try {
      await addTimeslot(doctorId, selectedDate, newTime);
      await loadTimeslots();
      setNewTime('');
    } catch (err) {
      console.error('Error adding timeslot:', err);
      alert('Failed to add timeslot');
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveTimeslot = async (slotId) => {
    if (!confirm('Remove this timeslot?')) return;
    try {
      await removeTimeslot(slotId);
      await loadTimeslots();
    } catch (err) {
      console.error('Error removing timeslot:', err);
      alert('Failed to remove timeslot');
    }
  };

  const isTimeBooked = (time) => {
    return appointments.some(appt => appt.date === selectedDate && appt.time === time);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-gray-800">Manage Available Timeslots</h2>
        <button
          onClick={onRefresh}
          className="text-blue-600 hover:text-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Date Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Date</label>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Add New Timeslot */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-700 mb-3">Add New Timeslot</h3>
        <div className="flex gap-3">
          <select
            value={newTime}
            onChange={(e) => setNewTime(e.target.value)}
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select time...</option>
            {timeOptions.map(time => (
              <option key={time} value={time} disabled={timeslots.some(s => s.time === time && s.is_available)}>
                {time} {timeslots.some(s => s.time === time && s.is_available) ? '(Already added)' : ''}
              </option>
            ))}
          </select>
          <button
            onClick={handleAddTimeslot}
            disabled={adding || !newTime}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium px-4 py-2 rounded-lg transition-colors"
          >
            {adding ? 'Adding...' : '+ Add'}
          </button>
        </div>
      </div>

      {/* Timeslots Grid */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading timeslots...</div>
      ) : (
        <div>
          <h3 className="font-medium text-gray-700 mb-3">Available Timeslots for {selectedDate}</h3>
          <div className="grid grid-cols-4 md:grid-cols-6 gap-3">
            {timeslots.filter(slot => slot.is_available).length === 0 ? (
              <div className="col-span-full text-center py-8 text-gray-500">
                No available timeslots for this date
              </div>
            ) : (
              timeslots.filter(slot => slot.is_available).map(slot => {
                const isBooked = isTimeBooked(slot.time);
                return (
                  <div
                    key={slot.id}
                    className={`relative p-3 rounded-lg text-center ${
                      isBooked
                        ? 'bg-red-100 text-red-700 border border-red-200'
                        : 'bg-green-100 text-green-700 border border-green-200'
                    }`}
                  >
                    <span className="font-medium">{slot.time}</span>
                    {!isBooked && (
                      <button
                        onClick={() => handleRemoveTimeslot(slot.id)}
                        className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-red-600"
                      >
                        ×
                      </button>
                    )}
                    {isBooked && (
                      <div className="text-xs mt-1 text-red-600">Booked</div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      <div className="mt-6 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> Green slots are available. Red slots are booked. Click the × to remove an available slot.
        </p>
      </div>
    </div>
  );
};

export default TimeslotManager;