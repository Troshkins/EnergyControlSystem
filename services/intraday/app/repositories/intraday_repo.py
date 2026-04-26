from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.intraday import (
    IntradayActionRecord,
    IntradayOptimizationResponse,
)


def get_intraday_actions(db: Session):
    query = text(
        """
        SELECT
            run_id,
            timestamp,
            action_type,
            amount,
            cost_impact,
            explanation
        FROM intraday_actions
        ORDER BY timestamp ASC
        """
    )
    return db.execute(query).mappings().all()


def get_intraday_actions_by_date(
    db: Session,
    action_date: date,
) -> list[IntradayActionRecord]:
    query = text(
        """
        SELECT
            run_id,
            timestamp,
            action_type,
            amount,
            CASE
                WHEN action_type IN ('battery_charge', 'sell_to_market', 'charge_and_sell')
                    THEN -amount
                ELSE amount
            END AS deviation,
            cost_impact,
            explanation
        FROM intraday_actions
        WHERE DATE(timestamp) = :action_date
        ORDER BY timestamp ASC, id ASC
        """
    )
    rows = db.execute(query, {"action_date": action_date}).mappings().all()
    return [
        IntradayActionRecord(
            run_id=row["run_id"],
            timestamp=row["timestamp"],
            action_type=row["action_type"],
            amount=float(row["amount"]) if row["amount"] is not None else 0.0,
            deviation=float(row["deviation"]) if row["deviation"] is not None else 0.0,
            cost_impact=float(row["cost_impact"]) if row["cost_impact"] is not None else 0.0,
            explanation=row["explanation"] or "",
        )
        for row in rows
    ]


def save_intraday_action(
    db: Session,
    response: IntradayOptimizationResponse,
):
    try:
        db.execute(
            text(
                """
                INSERT INTO intraday_actions (
                    run_id,
                    timestamp,
                    action_type,
                    amount,
                    cost_impact,
                    explanation
                )
                VALUES (
                    :run_id,
                    :timestamp,
                    :action_type,
                    :amount,
                    :cost_impact,
                    :explanation
                )
                """
            ),
            {
                "run_id": response.run_id,
                "timestamp": response.timestamp,
                "action_type": response.action_type,
                "amount": response.amount,
                "cost_impact": response.cost_impact,
                "explanation": response.explanation,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
