from sqlalchemy.orm import Session

from app.models.energy import EnergyAssets


def _dump(item):
    return item.model_dump() if hasattr(item, "model_dump") else item.dict()


def save_assets(db: Session, data):
    row = EnergyAssets(**_dump(data))
    db.add(row)
    db.commit()
