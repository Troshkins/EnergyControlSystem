// src/pages/RealTimePage.tsx
import { useEffect, useState } from 'react';
import { fetchIntraday } from '../api/api';
import type { IntradayAction } from '../api/api';
import { mockData } from '../data/mockData';

interface DisplayAction {
  time: string;
  action: string;
  cost: number;
  price: number;
}

export default function RealTimePage() {
  const [actions, setActions] = useState<DisplayAction[]>(mockData.intradayActions);

  useEffect(() => {
    fetchIntraday().then(data => {
      if (data && data.length > 0) {
        setActions(
          data.map((a: IntradayAction) => ({
            time: new Date(a.timestamp).toLocaleTimeString('ru', {
              hour: '2-digit',
              minute: '2-digit',
            }),
            action: `Actual demand: ${a.actual_demand} MWh`,
            cost: 0,
            price: 0,
          }))
        );
      }
    });
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Real-time Corrections (Intraday)</h1>

      <div className="bg-zinc-900 rounded-3xl p-6">
        <h2 className="text-xl font-semibold mb-6">Последние действия на intraday рынке</h2>
        <div className="space-y-4">
          {actions.map((action, i) => (
            <div key={i} className="flex items-center justify-between bg-zinc-800 p-5 rounded-2xl">
              <div>
                <div className="font-medium">{action.time}</div>
                <div className="text-zinc-400">{action.action}</div>
              </div>
              <div className="text-right">
                <div className={`text-xl font-bold ${action.cost > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {action.cost > 0 ? '+' : ''}{action.cost} €
                </div>
                <div className="text-xs text-zinc-500">{action.price} €/MWh</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
