from datetime import datetime
from typing import List

from pydantic import BaseModel


class PriceItem(BaseModel):
    timestamp: datetime
    price: float


class PriceInput(BaseModel):
    prices: List[PriceItem]


class ForecastItem(BaseModel):
    timestamp: datetime
    demand: float


class ForecastInput(BaseModel):
    forecast: List[ForecastItem]


class AssetsInput(BaseModel):
    battery_capacity: float
    max_charge: float
    max_discharge: float
    gas_max_output: float
    gas_cost: float


class IntradayInput(BaseModel):
    timestamp: datetime
    actual_demand: float
