from sqlalchemy import Column, DateTime, Float, Integer
from app.core.database import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    demand = Column(Float, nullable=False)


class EnergyAssets(Base):
    __tablename__ = "energy_assets"

    id = Column(Integer, primary_key=True, index=True)
    battery_capacity = Column(Float, nullable=False)
    max_charge = Column(Float, nullable=False)
    max_discharge = Column(Float, nullable=False)
    gas_max_output = Column(Float, nullable=False)
    gas_cost = Column(Float, nullable=False)


class IntradayAction(Base):
    __tablename__ = "intraday_actions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    actual_demand = Column(Float, nullable=False)
