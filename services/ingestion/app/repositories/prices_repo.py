from sqlalchemy.orm import Session
from app.models.energy import Price


def save_prices(db: Session, prices):
    rows = [
        Price(timestamp=p.timestamp, price=p.price)
        for p in prices
    ]
    db.add_all(rows)
    db.commit()
