from datetime import date
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_latest_day_ahead_schedule_for_date(
    db: Session,
    schedule_date: date,
):
    query = text(
        """
        WITH latest_run AS (
            SELECT run_id
            FROM day_ahead_schedules
            WHERE schedule_date = :schedule_date
            GROUP BY run_id
            ORDER BY MAX(created_at) DESC
            LIMIT 1
        )
        SELECT
            run_id,
            schedule_date,
            timestamp,
            hour,
            price,
            demand,
            grid_usage,
            gas_usage,
            battery_charge,
            battery_discharge,
            battery_soc,
            hour_cost
        FROM day_ahead_schedules
        WHERE run_id = (SELECT run_id FROM latest_run)
        ORDER BY hour ASC, timestamp ASC
        """
    )
    return db.execute(query, {"schedule_date": schedule_date}).mappings().all()


def get_day_ahead_schedule_by_run_id(
    db: Session,
    run_id: UUID,
):
    query = text(
        """
        SELECT
            run_id,
            schedule_date,
            timestamp,
            hour,
            price,
            demand,
            grid_usage,
            gas_usage,
            battery_charge,
            battery_discharge,
            battery_soc,
            hour_cost
        FROM day_ahead_schedules
        WHERE run_id = :run_id
        ORDER BY hour ASC, timestamp ASC
        """
    )
    return db.execute(query, {"run_id": run_id}).mappings().all()


def get_latest_asset_constraints(db: Session):
    battery = db.execute(
        text(
            """
            SELECT capacity, max_charge, max_discharge
            FROM energy_assets
            WHERE asset_type = 'battery'
            ORDER BY id DESC
            LIMIT 1
            """
        )
    ).fetchone()

    gas = db.execute(
        text(
            """
            SELECT max_output
            FROM energy_assets
            WHERE asset_type = 'gas'
            ORDER BY id DESC
            LIMIT 1
            """
        )
    ).fetchone()

    return {
        "battery_capacity": float(battery.capacity) if battery and battery.capacity is not None else 0.0,
        "max_charge": float(battery.max_charge) if battery and battery.max_charge is not None else 0.0,
        "max_discharge": float(battery.max_discharge) if battery and battery.max_discharge is not None else 0.0,
        "gas_max_output": float(gas.max_output) if gas and gas.max_output is not None else 0.0,
    }
