// src/pages/InputsPage.tsx
import { useEffect, useState } from 'react';
import { fetchPrices, fetchForecast, fetchAssets } from '../api/api';
import type { PriceItem, ForecastItem, AssetsData } from '../api/api';
import { mockData } from '../data/mockData';

export default function InputsPage() {
  const [prices, setPrices]     = useState<{ hour: number; price: number }[]>(mockData.prices);
  const [forecast, setForecast] = useState<{ hour: number; forecast: number }[]>(mockData.demandForecast);
  const [assets, setAssets]     = useState<AssetsData | null>(null);

  useEffect(() => {
    fetchPrices().then(data => {
      if (data && data.length > 0) {
        setPrices(
          data.map((p: PriceItem) => ({
            hour: new Date(p.timestamp).getHours(),
            price: p.price,
          }))
        );
      }
    });

    fetchForecast().then(data => {
      if (data && data.length > 0) {
        setForecast(
          data.map((f: ForecastItem) => ({
            hour: new Date(f.timestamp).getHours(),
            forecast: f.demand,
          }))
        );
      }
    });

    fetchAssets().then(data => {
      if (data) setAssets(data);
    });
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Inputs</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Prices */}
        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="font-semibold mb-4">Electricity Prices (24h)</h2>
          <div className="max-h-96 overflow-auto text-sm">
            {prices.map((p, i) => (
              <div key={i} className="flex justify-between py-2 border-b border-zinc-800 last:border-0">
                <span className="text-zinc-400">Hour {p.hour}</span>
                <span className="font-mono">{p.price} €/MWh</span>
              </div>
            ))}
          </div>
        </div>

        {/* Forecast */}
        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="font-semibold mb-4">Demand Forecast</h2>
          <div className="max-h-96 overflow-auto text-sm">
            {forecast.map((d, i) => (
              <div key={i} className="flex justify-between py-2 border-b border-zinc-800 last:border-0">
                <span className="text-zinc-400">Hour {d.hour}</span>
                <span className="font-mono">{d.forecast} MWh</span>
              </div>
            ))}
          </div>
        </div>

        {/* Assets */}
        <div className="bg-zinc-900 rounded-3xl p-6">
          <h2 className="font-semibold mb-4">Energy Assets</h2>
          <div className="space-y-6 text-sm">
            <div>
              <div className="text-emerald-400">Battery capacity</div>
              <div className="text-3xl font-bold">
                {assets ? assets.battery_capacity : 250} MWh
              </div>
            </div>
            <div>
              <div className="text-emerald-400">Max charge / discharge</div>
              <div className="text-3xl font-bold">
                {assets
                  ? `${assets.max_charge} MW / ${assets.max_discharge} MW`
                  : '80 MW / 80 MW'}
              </div>
            </div>
            <div>
              <div className="text-emerald-400">Gas max output</div>
              <div className="text-3xl font-bold">
                {assets ? assets.gas_max_output : 60} MW
              </div>
            </div>
            {assets && (
              <div>
                <div className="text-emerald-400">Gas cost</div>
                <div className="text-3xl font-bold">{assets.gas_cost} €/MWh</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
