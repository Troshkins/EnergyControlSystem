from sqlalchemy.orm import Session
from app.models.energy import DemandForecast


def save_forecast(db: Session, forecast):
    rows = [DemandForecast(timestamp=f.timestamp, demand=f.demand) for f in forecast]
    db.add_all(rows)
    db.commit()
