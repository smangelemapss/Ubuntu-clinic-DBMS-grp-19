const Sidebar = ({ open, onClose }) => {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-4">
      <nav className="space-y-2">
        <p className="text-sm text-gray-500">Navigation</p>
      </nav>
    </aside>
  );
};

export default Sidebar;
