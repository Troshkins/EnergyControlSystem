// src/api/api.ts

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function get<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${BASE_URL}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error(`GET ${path} failed:`, e);
    return null;
  }
}

// ─── Types (matching backend Pydantic schemas) ────────────────────────────────

export interface PriceItem {
  timestamp: string; // ISO datetime
  price: number;
}

export interface ForecastItem {
  timestamp: string; // ISO datetime
  demand: number;
}

export interface AssetsData {
  battery_capacity: number;
  max_charge: number;
  max_discharge: number;
  gas_max_output: number;
  gas_cost: number;
}

export interface IntradayAction {
  timestamp: string; // ISO datetime
  actual_demand: number;
}

// ─── API calls ────────────────────────────────────────────────────────────────

export const fetchPrices   = () => get<PriceItem[]>('/prices');
export const fetchForecast = () => get<ForecastItem[]>('/forecast');
export const fetchAssets   = () => get<AssetsData>('/assets');
export const fetchIntraday = () => get<IntradayAction[]>('/intraday');
