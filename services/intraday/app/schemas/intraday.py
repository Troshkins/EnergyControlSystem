from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class IntradayOptimizationRequest(BaseModel):
    timestamp: datetime
    actual_demand: float
    intraday_price: float | None = None
    run_id: UUID | None = None
    current_battery_soc: float | None = None


class UpdatedScheduleHour(BaseModel):
    timestamp: datetime
    hour: int
    planned_demand: float
    adjusted_grid_usage: float
    adjusted_gas_usage: float
    adjusted_battery_charge: float
    adjusted_battery_discharge: float
    adjusted_battery_soc: float
    note: str


class IntradayOptimizationResponse(BaseModel):
    run_id: UUID
    schedule_date: date
    timestamp: datetime
    hour: int
    planned_demand: float
    actual_demand: float
    deviation: float
    action_type: str
    amount: float
    cost_impact: float
    explanation: str
    updated_remaining_schedule: list[UpdatedScheduleHour]


class IntradayActionRecord(BaseModel):
    run_id: UUID | None = None
    timestamp: datetime
    action_type: str
    amount: float
    deviation: float
    cost_impact: float
    explanation: str


class IntradayActionListResponse(BaseModel):
    date: date
    actions: list[IntradayActionRecord]
