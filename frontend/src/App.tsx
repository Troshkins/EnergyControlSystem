// src/App.tsx
import { useState } from 'react';
import DashboardLayout from './components/DashboardLayout';

function App() {
  const [currentPage, setCurrentPage] = useState<'inputs' | 'schedule' | 'realtime' | 'tests'>('schedule');

  return (
    <DashboardLayout currentPage={currentPage} setCurrentPage={setCurrentPage} />
  );
}

export default App;
