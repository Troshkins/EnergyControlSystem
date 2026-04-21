from sqlalchemy.orm import Session
from app.models.energy import IntradayAction


def save_intraday(db: Session, data):
    row = IntradayAction(**data.dict())
    db.add(row)
    db.commit()
