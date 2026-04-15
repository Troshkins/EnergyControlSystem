// src/pages/InputsPage.tsx
import { mockData } from '../data/mockData';

export default function InputsPage() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Inputs</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="font-semibold mb-4">Electricity Prices (24h)</h2>
          <div className="max-h-96 overflow-auto text-sm">
            {mockData.prices.map((p, i) => (
              <div key={i} className="flex justify-between py-2 border-b border-zinc-800 last:border-0">
                <span className="text-zinc-400">Hour {p.hour}</span>
                <span className="font-mono">{p.price} €/MWh</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="font-semibold mb-4">Demand Forecast</h2>
          <div className="max-h-96 overflow-auto text-sm">
            {mockData.demandForecast.map((d, i) => (
              <div key={i} className="flex justify-between py-2 border-b border-zinc-800 last:border-0">
                <span className="text-zinc-400">Hour {d.hour}</span>
                <span className="font-mono">{d.forecast} MWh</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="font-semibold mb-4">Energy Assets</h2>
          <div className="space-y-6 text-sm">
            <div>
              <div className="text-emerald-400">Battery capacity</div>
              <div className="text-3xl font-bold">250 MWh</div>
            </div>
            <div>
              <div className="text-emerald-400">Max charge / discharge</div>
              <div className="text-3xl font-bold">80 MW / 80 MW</div>
            </div>
            <div>
              <div className="text-emerald-400">Gas max output</div>
              <div className="text-3xl font-bold">60 MW</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
