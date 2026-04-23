from sqlalchemy.orm import Session

from app.models.energy import IntradayAction


def _dump(item):
    return item.model_dump() if hasattr(item, "model_dump") else item.dict()


def save_intraday(db: Session, data):
    row = IntradayAction(**_dump(data))
    db.add(row)
    db.commit()
