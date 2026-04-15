// src/components/DashboardLayout.tsx
import { useState } from 'react';
import Sidebar from './Sidebar';
import InputsPage from '../pages/InputsPage';
import SchedulePage from '../pages/SchedulePage';
import RealTimePage from '../pages/RealTimePage';
import TestsPage from '../pages/TestsPage';

export default function DashboardLayout({ 
  currentPage, 
  setCurrentPage 
}: { 
  currentPage: 'inputs' | 'schedule' | 'realtime' | 'tests';
  setCurrentPage: (page: 'inputs' | 'schedule' | 'realtime' | 'tests') => void;
}) {
  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      {/* Sidebar */}
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-8">
        {currentPage === 'inputs' && <InputsPage />}
        {currentPage === 'schedule' && <SchedulePage />}
        {currentPage === 'realtime' && <RealTimePage />}
        {currentPage === 'tests' && <TestsPage />}
      </div>
    </div>
  );
}
