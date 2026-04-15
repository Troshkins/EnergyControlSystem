// src/components/Sidebar.tsx
import { Home, BarChart3, Clock, TestTube } from 'lucide-react';

const menuItems = [
  { id: 'schedule', label: 'Daily Schedule', icon: BarChart3 },
  { id: 'inputs', label: 'Inputs', icon: Home },
  { id: 'realtime', label: 'Real-time Corrections', icon: Clock },
  { id: 'tests', label: 'Test Scenarios', icon: TestTube },
] as const;

export default function Sidebar({ 
  currentPage, 
  setCurrentPage 
}: { 
  currentPage: 'inputs' | 'schedule' | 'realtime' | 'tests';
  setCurrentPage: (page: 'inputs' | 'schedule' | 'realtime' | 'tests') => void;
}) {
  return (
    <div className="w-72 bg-zinc-900 border-r border-zinc-800 flex flex-col">
      <div className="p-6 border-b border-zinc-800">
        <h1 className="text-2xl font-bold text-emerald-400">ECS Dashboard</h1>
        <p className="text-zinc-500 text-sm mt-1">Energy Control System</p>
      </div>

      <nav className="flex-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all ${
                isActive 
                  ? 'bg-emerald-600 text-white' 
                  : 'hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-zinc-800 text-xs text-zinc-500">
        Energy Control System • Group Project
      </div>
    </div>
  );
}
