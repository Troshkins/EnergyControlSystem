// src/pages/SchedulePage.tsx
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { mockData } from '../data/mockData';

export default function SchedulePage() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-white">Daily Schedule (Day-Ahead)</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Цены и спрос */}
        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="text-xl font-semibold mb-4">Electricity Price vs Demand</h2>
          <ResponsiveContainer width="100%" height={340}>
            <LineChart data={mockData.prices}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="hour" stroke="#a3a3a3" />
              <YAxis stroke="#a3a3a3" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="price" stroke="#10b981" strokeWidth={3} name="Цена (€/MWh)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Расписание по источникам */}
        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="text-xl font-semibold mb-4">Energy Sources Schedule</h2>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={mockData.dayAheadSchedule}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="hour" stroke="#a3a3a3" />
              <YAxis stroke="#a3a3a3" />
              <Tooltip />
              <Legend />
              <Bar dataKey="grid" stackId="a" fill="#10b981" name="Grid" />
              <Bar dataKey="gas" stackId="a" fill="#eab308" name="Gas" />
              <Bar dataKey="battery" stackId="a" fill="#06b67f" name="Battery" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Состояние батареи */}
      <div className="bg-zinc-900 rounded-3xl p-6 flex items-center gap-8">
        <div className="flex-1">
          <h2 className="text-xl font-semibold mb-2">Battery State of Charge</h2>
          <div className="h-4 bg-zinc-800 rounded-2xl overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 transition-all"
              style={{ width: `${mockData.batterySOC}%` }}
            />
          </div>
        </div>
        <div className="text-6xl font-bold text-emerald-400 w-28 text-right">
          {mockData.batterySOC}%
        </div>
      </div>
    </div>
  );
}
