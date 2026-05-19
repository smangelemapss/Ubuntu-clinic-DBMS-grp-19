import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CalendarDays,
  ClipboardList,
  Users,
  Pill,
  FileText,
  BarChart2,
  Settings,
  X,
  Stethoscope,
} from 'lucide-react';

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', to: '/', icon: <LayoutDashboard size={18} /> },
  { label: 'Appointments', to: '/appointments', icon: <CalendarDays size={18} /> },
  { label: 'Consultations', to: '/consultations', icon: <ClipboardList size={18} /> },
  { label: 'Patients', to: '/patients', icon: <Users size={18} /> },
  { label: 'Pharmacy', to: '/pharmacy', icon: <Pill size={18} /> },
  { label: 'Records', to: '/records', icon: <FileText size={18} /> },
  { label: 'Reports', to: '/reports', icon: <BarChart2 size={18} /> },
];

const bottomItems: NavItem[] = [
  { label: 'Settings', to: '/settings', icon: <Settings size={18} /> },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* Backdrop (mobile) */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={[
          'fixed top-0 left-0 h-full w-64 bg-slate-900 flex flex-col z-30 transition-transform duration-300 ease-in-out',
          'lg:translate-x-0 lg:static lg:z-auto',
          open ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-700/50 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-teal-500 rounded-lg flex items-center justify-center">
              <Stethoscope size={17} className="text-white" />
            </div>
            <div className="leading-tight">
              <p className="text-white text-sm font-semibold">Ubuntu</p>
              <p className="text-teal-400 text-xs font-bold tracking-wider uppercase">Campus Clinic</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:bg-slate-800 hover:text-white transition-colors lg:hidden"
          >
            <X size={18} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
          <p className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-3 mb-2">
            Main Menu
          </p>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={onClose}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150',
                  isActive
                    ? 'bg-teal-600/20 text-teal-400 border border-teal-600/30'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white',
                ].join(' ')
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Bottom nav */}
        <div className="shrink-0 border-t border-slate-700/50 py-3 px-3 space-y-0.5">
          {bottomItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150',
                  isActive
                    ? 'bg-teal-600/20 text-teal-400 border border-teal-600/30'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white',
                ].join(' ')
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </div>
      </aside>
    </>
  );
}
