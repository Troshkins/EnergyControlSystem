from datetime import date
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.optimization import AssetConstraints
from app.schemas.optimization import DayAheadOptimizationResponse, SavedScheduleRun, ScheduleHour


def save_day_ahead_schedule(
    db: Session,
    run_id: UUID,
    optimization_response: DayAheadOptimizationResponse,
) -> None:
    if not optimization_response.schedule:
        raise ValueError("Optimization response does not contain schedule rows.")

    schedule_date = optimization_response.schedule[0].timestamp.date()

    try:
        db.execute(
            text(
                """
                INSERT INTO simulation_runs (id, run_type, status, total_cost)
                VALUES (:id, :run_type, :status, :total_cost)
                ON CONFLICT (id) DO UPDATE
                SET
                    run_type = EXCLUDED.run_type,
                    status = EXCLUDED.status,
                    total_cost = EXCLUDED.total_cost
                """
            ),
            {
                "id": run_id,
                "run_type": "day_ahead",
                "status": optimization_response.status,
                "total_cost": optimization_response.total_cost,
            },
        )

        insert_schedule_query = text(
            """
            INSERT INTO day_ahead_schedules (
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
            )
            VALUES (
                :run_id,
                :schedule_date,
                :timestamp,
                :hour,
                :price,
                :demand,
                :grid_usage,
                :gas_usage,
                :battery_charge,
                :battery_discharge,
                :battery_soc,
                :hour_cost
            )
            """
        )

        for row in optimization_response.schedule:
            db.execute(
                insert_schedule_query,
                {
                    "run_id": run_id,
                    "schedule_date": schedule_date,
                    "timestamp": row.timestamp,
                    "hour": row.hour,
                    "price": row.price,
                    "demand": row.demand,
                    "grid_usage": row.grid_usage,
                    "gas_usage": row.gas_usage,
                    "battery_charge": row.battery_charge,
                    "battery_discharge": row.battery_discharge,
                    "battery_soc": row.battery_soc,
                    "hour_cost": row.hour_cost,
                },
            )

        db.commit()
    except Exception:
        db.rollback()
        raise


def get_schedule_runs_by_date(
    db: Session,
    schedule_date: date,
) -> list[SavedScheduleRun]:
    query = text(
        """
        SELECT
            ds.run_id,
            ds.schedule_date,
            ds.timestamp,
            ds.hour,
            ds.price,
            ds.demand,
            ds.grid_usage,
            ds.gas_usage,
            ds.battery_charge,
            ds.battery_discharge,
            ds.battery_soc,
            ds.hour_cost,
            COALESCE(sr.status, 'saved') AS status,
            sr.total_cost
        FROM day_ahead_schedules ds
        LEFT JOIN simulation_runs sr
            ON sr.id = ds.run_id
        WHERE ds.schedule_date = :schedule_date
        ORDER BY ds.run_id, ds.hour ASC, ds.timestamp ASC
        """
    )
    rows = db.execute(query, {"schedule_date": schedule_date}).mappings().all()
    return _group_schedule_rows(rows)


def get_latest_schedule_run_by_date(
    db: Session,
    schedule_date: date,
) -> SavedScheduleRun | None:
    query = text(
        """
        WITH latest_run AS (
            SELECT ds.run_id
            FROM day_ahead_schedules ds
            LEFT JOIN simulation_runs sr
                ON sr.id = ds.run_id
            WHERE ds.schedule_date = :schedule_date
            GROUP BY ds.run_id
            ORDER BY
                MAX(COALESCE(sr.created_at, ds.created_at)) DESC,
                MAX(ds.created_at) DESC
            LIMIT 1
        )
        SELECT
            ds.run_id,
            ds.schedule_date,
            ds.timestamp,
            ds.hour,
            ds.price,
            ds.demand,
            ds.grid_usage,
            ds.gas_usage,
            ds.battery_charge,
            ds.battery_discharge,
            ds.battery_soc,
            ds.hour_cost,
            COALESCE(sr.status, 'saved') AS status,
            sr.total_cost
        FROM day_ahead_schedules ds
        LEFT JOIN simulation_runs sr
            ON sr.id = ds.run_id
        INNER JOIN latest_run lr
            ON lr.run_id = ds.run_id
        ORDER BY ds.hour ASC, ds.timestamp ASC
        """
    )
    rows = db.execute(query, {"schedule_date": schedule_date}).mappings().all()
    grouped = _group_schedule_rows(rows)
    if not grouped:
        return None
    return grouped[0]


def get_latest_asset_constraints(db: Session) -> AssetConstraints | None:
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

    if battery is None and gas is None:
        return None

    return AssetConstraints(
        battery_capacity=float(battery.capacity) if battery and battery.capacity is not None else 0.0,
        max_charge=float(battery.max_charge) if battery and battery.max_charge is not None else 0.0,
        max_discharge=float(battery.max_discharge) if battery and battery.max_discharge is not None else 0.0,
        gas_max_output=float(gas.max_output) if gas and gas.max_output is not None else 0.0,
        gas_cost=settings.DEFAULT_GAS_COST,
        initial_battery_soc=settings.DEFAULT_INITIAL_BATTERY_SOC,
    )


def _group_schedule_rows(rows) -> list[SavedScheduleRun]:
    grouped_runs: dict[UUID, dict] = {}

    for row in rows:
        run_id = row["run_id"]
        if run_id not in grouped_runs:
            grouped_runs[run_id] = {
                "run_id": run_id,
                "date": row["schedule_date"],
                "status": row["status"],
                "total_cost": float(row["total_cost"]) if row["total_cost"] is not None else 0.0,
                "schedule": [],
            }

        grouped_runs[run_id]["schedule"].append(
            ScheduleHour(
                timestamp=row["timestamp"],
                hour=row["hour"],
                price=float(row["price"]),
                demand=float(row["demand"]),
                grid_usage=float(row["grid_usage"]),
                gas_usage=float(row["gas_usage"]),
                battery_charge=float(row["battery_charge"]),
                battery_discharge=float(row["battery_discharge"]),
                battery_soc=float(row["battery_soc"]),
                hour_cost=float(row["hour_cost"]),
            )
        )

    result = []
    for run in grouped_runs.values():
        if run["total_cost"] == 0.0 and run["schedule"]:
            run["total_cost"] = sum(hour.hour_cost for hour in run["schedule"])
        result.append(SavedScheduleRun(**run))

    return result
