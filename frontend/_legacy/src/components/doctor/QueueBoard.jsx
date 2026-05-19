// frontend/src/components/doctor/QueueBoard.jsx
import { useState } from 'react';
import { updateQueueStatus, callNextPatient } from '../../services/api';

// Import F2-style data structures (mock integration)
// In production, these would come from the API with patient data from F2 modules
const QueueBoard = ({ queueEntries, doctorId, onStatusUpdate }) => {
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [callingNext, setCallingNext] = useState(false);

  // Sort queue: URGENT first, then IN_PROGRESS, then WAITING by check-in time
  const sortedQueue = [...queueEntries].sort((a, b) => {
    const priorityOrder = { URGENT: 0, NORMAL: 1 };
    const statusOrder = { IN_PROGRESS: 0, WAITING: 1, COMPLETED: 2, LEFT_WITHOUT_SEEN: 3 };
    
    if (a.priority !== b.priority) {
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    }
    if (a.status !== b.status) {
      return statusOrder[a.status] - statusOrder[b.status];
    }
    return new Date(a.check_in_time) - new Date(b.check_in_time);
  });

  const waitingCount = queueEntries.filter(q => q.status === 'WAITING').length;
  const inProgressCount = queueEntries.filter(q => q.status === 'IN_PROGRESS').length;
  const urgentCount = queueEntries.filter(q => q.priority === 'URGENT' && q.status !== 'COMPLETED').length;

  const handleStatusChange = async (entryId, newStatus) => {
    setUpdating(true);
    try {
      await updateQueueStatus(entryId, { status: newStatus });
      await onStatusUpdate();
    } catch (error) {
      console.error('Error updating queue status:', error);
      alert('Failed to update patient status. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const handleCallNext = async () => {
    setCallingNext(true);
    try {
      await callNextPatient(doctorId);
      await onStatusUpdate();
    } catch (error) {
      console.error('Error calling next patient:', error);
      alert('Failed to call next patient. Please try again.');
    } finally {
      setCallingNext(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      WAITING: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Waiting' },
      IN_PROGRESS: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'In Progress' },
      COMPLETED: { bg: 'bg-green-100', text: 'text-green-800', label: 'Completed' },
      LEFT_WITHOUT_SEEN: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Left' }
    };
    const style = styles[status] || styles.WAITING;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text}`}>
        {style.label}
      </span>
    );
  };

  const getPriorityBadge = (priority) => {
    if (priority === 'URGENT') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          🚨 Urgent
        </span>
      );
    }
    return (
      <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
        Normal
      </span>
    );
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-yellow-500">
          <p className="text-2xl font-bold text-gray-800">{waitingCount}</p>
          <p className="text-sm text-gray-500">Waiting</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
          <p className="text-2xl font-bold text-gray-800">{inProgressCount}</p>
          <p className="text-sm text-gray-500">In Consultation</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-red-500">
          <p className="text-2xl font-bold text-gray-800">{urgentCount}</p>
          <p className="text-sm text-gray-500">Urgent Cases</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
          <button
            onClick={handleCallNext}
            disabled={callingNext || waitingCount === 0}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
            {callingNext ? 'Calling...' : 'Call Next Patient'}
          </button>
        </div>
      </div>

      {/* Queue Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Check-in Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reason
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedQueue.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                    No patients in queue
                  </td>
                </tr>
              ) : (
                sortedQueue.map((entry, index) => (
                  <tr
                    key={entry.id}
                    className={`hover:bg-gray-50 cursor-pointer ${entry.status === 'IN_PROGRESS' ? 'bg-blue-50' : ''}`}
                    onClick={() => setSelectedPatient(selectedPatient?.id === entry.id ? null : entry)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{entry.patient_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {entry.student_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatTime(entry.check_in_time)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getPriorityBadge(entry.priority)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {entry.reason || 'Not specified'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(entry.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        {entry.status === 'WAITING' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusChange(entry.id, 'IN_PROGRESS');
                            }}
                            disabled={updating}
                            className="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            Start
                          </button>
                        )}
                        {entry.status === 'IN_PROGRESS' && (
                          <>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStatusChange(entry.id, 'COMPLETED');
                              }}
                              disabled={updating}
                              className="text-green-600 hover:text-green-800 font-medium"
                            >
                              Complete
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStatusChange(entry.id, 'LEFT_WITHOUT_SEEN');
                              }}
                              disabled={updating}
                              className="text-gray-600 hover:text-gray-800 font-medium"
                            >
                              Skip
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Active Consult Panel - F3 Active Consult View using F2 MedicalHistory style */}
      {selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-800">Active Consultation</h2>
              <button
                onClick={() => setSelectedPatient(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6">
              {/* Patient Info Header */}
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">{selectedPatient.patient_name}</h3>
                    <p className="text-gray-600">Student ID: {selectedPatient.student_number}</p>
                    <p className="text-gray-600">Check-in: {formatTime(selectedPatient.check_in_time)}</p>
                  </div>
                  {getPriorityBadge(selectedPatient.priority)}
                </div>
              </div>

              {/* Reason for Visit */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-2">Reason for Visit</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-800">{selectedPatient.reason || 'Not specified'}</p>
                </div>
              </div>

              {/* Medical History Section - F3 using F2 MedicalHistory.jsx data structure */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Medical History</h4>
                <div className="space-y-3">
                  {/* This would come from F2 MedicalHistory component data */}
                  <div className="border border-gray-200 rounded-lg p-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-800">Previous Visit: 2025-04-10</p>
                        <p className="text-sm text-gray-600">Dr. Nkosi</p>
                      </div>
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">General</span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">Diagnosis: Tension headache</p>
                    <p className="text-sm text-gray-500 mt-1">Prescription: Rest and hydration</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-800">Previous Visit: 2025-03-22</p>
                        <p className="text-sm text-gray-600">Dr. Patel</p>
                      </div>
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">Mental Health</span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">Diagnosis: Mild anxiety</p>
                    <p className="text-sm text-gray-500 mt-1">Prescription: Counselling referral</p>
                  </div>
                </div>
                <button className="mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium">
                  + View Full History
                </button>
              </div>

              {/* Emergency Contacts - F3 using F2 EmergencyContacts.jsx data */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Emergency Contacts</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                    <div>
                      <p className="font-medium text-gray-800">Thabo Dlamini</p>
                      <p className="text-sm text-gray-600">Father • Emergency</p>
                    </div>
                    <a href="tel:0712345678" className="text-blue-600 hover:text-blue-700">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </a>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div>
                      <p className="font-medium text-gray-800">Nomsa Dlamini</p>
                      <p className="text-sm text-gray-600">Mother • Home</p>
                    </div>
                    <a href="tel:0829876543" className="text-blue-600 hover:text-blue-700">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </a>
                  </div>
                </div>
              </div>

              {/* Consultation Notes */}
              <div className="mb-6">
                <label className="block font-medium text-gray-700 mb-2">Consultation Notes</label>
                <textarea
                  rows="4"
                  className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Record diagnosis, prescription, and notes here..."
                ></textarea>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    handleStatusChange(selectedPatient.id, 'COMPLETED');
                    setSelectedPatient(null);
                  }}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Complete & Save
                </button>
                <button
                  onClick={() => setSelectedPatient(null)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueueBoard;