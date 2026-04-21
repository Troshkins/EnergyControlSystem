from sqlalchemy.orm import Session
from app.models.energy import EnergyAssets


def save_assets(db: Session, data):
    asset = EnergyAssets(**data.dict())
    db.add(asset)
    db.commit()
