from sqlalchemy.orm import Session

from app.models.energy import DemandForecast


def _dump(item):
    return item.model_dump() if hasattr(item, "model_dump") else item.dict()


def save_forecast(db: Session, forecast):
    rows = [DemandForecast(**_dump(item)) for item in forecast]
    db.add_all(rows)
    db.commit()
