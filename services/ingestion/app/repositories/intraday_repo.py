from sqlalchemy import text
from sqlalchemy.orm import Session


def save_intraday(db: Session, data):
    db.execute(text("""
        INSERT INTO intraday_actions (timestamp, action_type, amount)
        VALUES (:timestamp, :action_type, :amount)
    """), {
        "timestamp": data.timestamp,
        "action_type": "demand",
        "amount": data.actual_demand,
    })
    db.commit()


def get_intraday_actions(db: Session):
    rows = db.execute(text("""
        SELECT timestamp, action_type, amount
        FROM intraday_actions
        ORDER BY timestamp ASC
    """)).fetchall()

    return [
        {
            "timestamp": row.timestamp,
            "action_type": row.action_type,
            "actual_demand": float(row.amount) if row.amount else 0,
        }
        for row in rows
    ]
