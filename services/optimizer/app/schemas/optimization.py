from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PricePoint(BaseModel):
    timestamp: datetime
    price: float


class DemandPoint(BaseModel):
    timestamp: datetime
    demand: float


class AssetConstraints(BaseModel):
    battery_capacity: float
    max_charge: float
    max_discharge: float
    gas_max_output: float
    gas_cost: float
    initial_battery_soc: float = 0.0


class DayAheadOptimizationRequest(BaseModel):
    prices: list[PricePoint]
    demand_forecast: list[DemandPoint]
    asset_constraints: AssetConstraints


class ScheduleHour(BaseModel):
    timestamp: datetime
    hour: int
    price: float
    demand: float
    grid_usage: float
    gas_usage: float
    battery_charge: float
    battery_discharge: float
    battery_soc: float
    hour_cost: float


class DayAheadOptimizationResponse(BaseModel):
    status: str
    explanation: str
    total_cost: float
    schedule: list[ScheduleHour]
    run_id: UUID | None = None


class SavedScheduleRun(BaseModel):
    run_id: UUID
    date: date
    status: str
    total_cost: float
    schedule: list[ScheduleHour]


class ScheduleLookupResponse(BaseModel):
    date: date
    status: str
    run: SavedScheduleRun | None = None
    runs: list[SavedScheduleRun] | None = None
