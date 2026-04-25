from sqlalchemy.orm import Session

from app.models.energy import Price


def _dump(item):
    return item.model_dump() if hasattr(item, "model_dump") else item.dict()


def save_prices(db: Session, prices):
    rows = [Price(**_dump(item)) for item in prices]
    db.add_all(rows)
    db.commit()


def get_latest_prices(db: Session):
    rows = db.query(Price).order_by(Price.timestamp.asc()).all()
    return [{"timestamp": row.timestamp, "price": row.price} for row in rows]
