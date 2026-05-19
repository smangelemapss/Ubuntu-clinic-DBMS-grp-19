// frontend/src/pages/doctor/Dashboard.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import DoctorCalendar from '../../components/doctor/DoctorCalendar';
import TimeslotManager from '../../components/doctor/TimeslotManager';
import BookingForm from '../../components/doctor/BookingForm';
import QRDisplay from '../../components/doctor/QRDisplay';
import QueueBoard from '../../components/doctor/QueueBoard';
import {
  getDoctorAppointments,
  getQueueEntries,
  getNotifications,
  markNotificationRead,
  getUnreadCount
} from '../../services/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('queue');
  const [appointments, setAppointments] = useState([]);
  const [queueEntries, setQueueEntries] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Doctor info from JWT user or defaults
  const doctorInfo = {
    id: user?.id || 1,
    name: user?.name || user?.username || 'Dr. J. Sithole',
    specialization: user?.specialization || 'General Practitioner',
    room: user?.room || 'Room 101',
    email: user?.email || 'doctor@ubuntuclinic.com'
  };

  // Fetch all data
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [apptsData, queueData, notificationsData, unreadData] = await Promise.all([
        getDoctorAppointments(),
        getQueueEntries(doctorInfo.id),
        getNotifications(),
        getUnreadCount()
      ]);
      setAppointments(apptsData);
      setQueueEntries(queueData);
      setNotifications(notificationsData);
      setUnreadCount(unreadData.count || 0);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Refresh queue every 30 seconds
    const interval = setInterval(() => {
      getQueueEntries(doctorInfo.id).then(setQueueEntries).catch(console.error);
    }, 30000);
    return () => clearInterval(interval);
  }, [doctorInfo.id]);

  const handleQueueUpdate = async () => {
    const freshQueue = await getQueueEntries(doctorInfo.id);
    setQueueEntries(freshQueue);
  };

  const handleNotificationRead = async (id) => {
    await markNotificationRead(id);
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const handleMarkAllRead = async () => {
    const unreadIds = notifications.filter(n => !n.read).map(n => n.id);
    await Promise.all(unreadIds.map(id => markNotificationRead(id)));
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const tabs = [
    { id: 'queue', label: 'Queue Board', icon: '👥' },
    { id: 'calendar', label: 'Calendar', icon: '📅' },
    { id: 'booking', label: 'Book Appointment', icon: '📝' },
    { id: 'timeslots', label: 'Manage Slots', icon: '⏰' },
    { id: 'qr', label: 'QR Code', icon: '📱' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Doctor Dashboard</h1>
              <p className="text-gray-500 text-sm">
                {doctorInfo.name} • {doctorInfo.specialization} • {doctorInfo.room}
              </p>
            </div>
            <div className="flex items-center gap-4">
              {/* Notifications Bell */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Dropdown */}
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                    <div className="p-3 border-b border-gray-200 flex justify-between items-center">
                      <h3 className="font-semibold text-gray-800">Notifications</h3>
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-xs text-blue-600 hover:text-blue-700"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.length === 0 ? (
                        <div className="p-4 text-center text-gray-500">
                          No notifications
                        </div>
                      ) : (
                        notifications.map(notif => (
                          <div
                            key={notif.id}
                            className={`p-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors ${
                              !notif.read ? 'bg-blue-50' : ''
                            }`}
                            onClick={() => handleNotificationRead(notif.id)}
                          >
                            <p className="font-medium text-gray-800 text-sm">{notif.title}</p>
                            <p className="text-gray-600 text-xs mt-1">{notif.text}</p>
                            <p className="text-gray-400 text-xs mt-1">
                              {new Date(notif.time).toLocaleString()}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Doctor Avatar */}
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                  {doctorInfo.name.charAt(0)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 bg-white px-6">
        <div className="flex gap-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 font-medium text-sm transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Queue Board Tab */}
        {activeTab === 'queue' && (
          <QueueBoard
            queueEntries={queueEntries}
            doctorId={doctorInfo.id}
            onStatusUpdate={handleQueueUpdate}
          />
        )}

        {/* Calendar Tab */}
        {activeTab === 'calendar' && (
          <DoctorCalendar
            appointments={appointments}
            doctorId={doctorInfo.id}
            onRefresh={fetchData}
          />
        )}

        {/* Booking Form Tab */}
        {activeTab === 'booking' && (
          <BookingForm
            doctorId={doctorInfo.id}
            doctorName={doctorInfo.name}
            onBookingSuccess={() => {
              fetchData();
              setActiveTab('queue');
            }}
          />
        )}

        {/* Timeslot Manager Tab */}
        {activeTab === 'timeslots' && (
          <TimeslotManager
            doctorId={doctorInfo.id}
            appointments={appointments}
            onRefresh={fetchData}
          />
        )}

        {/* QR Display Tab */}
        {activeTab === 'qr' && (
          <QRDisplay
            doctorId={doctorInfo.id}
            doctorName={doctorInfo.name}
          />
        )}
      </main>
    </div>
  );
};

export default Dashboard;