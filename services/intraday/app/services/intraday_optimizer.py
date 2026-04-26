import logging

from app.core.config import settings
from app.producers.kafka_producer import kafka_producer
from app.repositories.intraday_repo import save_intraday_action
from app.repositories.schedule_repo import (
    get_day_ahead_schedule_by_run_id,
    get_latest_asset_constraints,
    get_latest_day_ahead_schedule_for_date,
)
from app.schemas.intraday import (
    IntradayOptimizationRequest,
    IntradayOptimizationResponse,
    UpdatedScheduleHour,
)

logger = logging.getLogger(__name__)


def optimize_intraday_update(
    request: IntradayOptimizationRequest,
    db,
) -> IntradayOptimizationResponse:
    if request.actual_demand < 0:
        raise ValueError("actual_demand must be greater than or equal to 0.")

    update_date = request.timestamp.date()
    current_hour = request.timestamp.hour

    schedule_rows = (
        get_day_ahead_schedule_by_run_id(db, request.run_id)
        if request.run_id is not None
        else get_latest_day_ahead_schedule_for_date(db, update_date)
    )
    if not schedule_rows:
        raise ValueError(f"No day-ahead schedule found for {update_date.isoformat()}.")

    run_id = schedule_rows[0]["run_id"]
    schedule_date = schedule_rows[0]["schedule_date"]
    current_row = next((row for row in schedule_rows if row["hour"] == current_hour), None)
    if current_row is None:
        raise ValueError(
            f"No planned schedule row found for hour {current_hour} on {update_date.isoformat()}."
        )

    planned_demand = float(current_row["demand"])
    deviation = request.actual_demand - planned_demand
    if deviation == 0:
        action_type = "no_action"
    elif deviation > 0:
        action_type = "cover_shortfall"
    else:
        action_type = "absorb_surplus"

    asset_constraints = get_latest_asset_constraints(db)
    battery_capacity = asset_constraints["battery_capacity"]
    current_battery_soc = (
        request.current_battery_soc
        if request.current_battery_soc is not None
        else float(current_row["battery_soc"])
    )
    if current_battery_soc < 0:
        raise ValueError("current_battery_soc must be greater than or equal to 0.")
    if battery_capacity > 0 and current_battery_soc > battery_capacity:
        raise ValueError("current_battery_soc cannot exceed battery capacity.")

    correction = _simulate_correction(
        deviation=deviation,
        current_battery_soc=current_battery_soc,
        asset_constraints=asset_constraints,
        intraday_price=request.intraday_price,
    )

    updated_remaining_schedule = _build_updated_remaining_schedule(
        schedule_rows=schedule_rows,
        current_hour=current_hour,
        current_battery_soc=current_battery_soc,
        correction=correction,
    )

    explanation = _build_explanation(
        action_type=correction["action_type"],
        deviation=deviation,
        battery_amount=correction["battery_amount"],
        gas_amount=correction["gas_amount"],
        market_amount=correction["market_amount"],
        charge_amount=correction["charge_amount"],
        curtailment_amount=correction["curtailment_amount"],
        intraday_price=request.intraday_price,
    )

    response = IntradayOptimizationResponse(
        run_id=run_id,
        schedule_date=schedule_date,
        timestamp=request.timestamp,
        hour=current_hour,
        planned_demand=planned_demand,
        actual_demand=request.actual_demand,
        deviation=deviation,
        action_type=correction["action_type"],
        amount=correction["amount"],
        cost_impact=correction["cost_impact"],
        explanation=explanation,
        updated_remaining_schedule=updated_remaining_schedule,
    )

    save_intraday_action(db, response)
    try:
        kafka_producer.send(
            topic=settings.KAFKA_INTRADAY_TOPIC,
            message=response.model_dump(mode="json"),
            key=str(run_id),
        )
    except Exception:
        logger.exception("Intraday action was saved but Kafka publish failed")

    return response


def _simulate_correction(
    deviation: float,
    current_battery_soc: float,
    asset_constraints: dict,
    intraday_price: float | None,
):
    battery_capacity = asset_constraints["battery_capacity"]
    max_charge = asset_constraints["max_charge"]
    max_discharge = asset_constraints["max_discharge"]
    gas_max_output = asset_constraints["gas_max_output"]

    battery_amount = 0.0
    gas_amount = 0.0
    market_amount = 0.0
    charge_amount = 0.0
    curtailment_amount = 0.0
    action_type = "no_action"
    cost_impact = 0.0

    if deviation > 0:
        remaining = deviation
        battery_amount = min(remaining, max_discharge, max(current_battery_soc, 0.0))
        remaining -= battery_amount

        gas_amount = min(remaining, gas_max_output)
        remaining -= gas_amount

        market_amount = max(remaining, 0.0)
        action_type = (
            "battery_discharge"
            if battery_amount > 0 and gas_amount == 0 and market_amount == 0
            else "mixed_supply"
        )
        if gas_amount == 0 and battery_amount == 0 and market_amount > 0:
            action_type = "buy_from_market"

        market_price = intraday_price if intraday_price is not None else 0.0
        cost_impact = (gas_amount * settings.DEFAULT_GAS_COST) + (market_amount * market_price)

    elif deviation < 0:
        surplus = abs(deviation)
        available_capacity = max(battery_capacity - current_battery_soc, 0.0)
        charge_amount = min(surplus, max_charge, available_capacity)
        surplus -= charge_amount

        curtailment_amount = max(surplus, 0.0)
        action_type = "battery_charge" if charge_amount > 0 else "sell_to_market"
        if charge_amount > 0 and curtailment_amount > 0:
            action_type = "charge_and_sell"

        market_price = intraday_price if intraday_price is not None else 0.0
        cost_impact = -(curtailment_amount * market_price)

    return {
        "action_type": action_type,
        "amount": abs(deviation),
        "cost_impact": cost_impact,
        "battery_amount": battery_amount,
        "gas_amount": gas_amount,
        "market_amount": market_amount,
        "charge_amount": charge_amount,
        "curtailment_amount": curtailment_amount,
    }


def _build_updated_remaining_schedule(
    schedule_rows,
    current_hour: int,
    current_battery_soc: float,
    correction: dict,
):
    updated_schedule = []
    adjusted_soc = current_battery_soc - correction["battery_amount"] + correction["charge_amount"]

    for row in schedule_rows:
        hour = int(row["hour"])
        if hour < current_hour:
            continue

        note = "Unchanged from day-ahead schedule."
        adjusted_grid_usage = float(row["grid_usage"])
        adjusted_gas_usage = float(row["gas_usage"])
        adjusted_battery_charge = float(row["battery_charge"])
        adjusted_battery_discharge = float(row["battery_discharge"])

        if hour == current_hour:
            adjusted_gas_usage += correction["gas_amount"]
            adjusted_battery_charge += correction["charge_amount"]
            adjusted_battery_discharge += correction["battery_amount"]
            adjusted_grid_usage += correction["market_amount"]
            note = (
                "Current hour adjusted using intraday corrective action. "
                "Future hours remain on the day-ahead plan."
            )

        updated_schedule.append(
            UpdatedScheduleHour(
                timestamp=row["timestamp"],
                hour=hour,
                planned_demand=float(row["demand"]),
                adjusted_grid_usage=adjusted_grid_usage,
                adjusted_gas_usage=adjusted_gas_usage,
                adjusted_battery_charge=adjusted_battery_charge,
                adjusted_battery_discharge=adjusted_battery_discharge,
                adjusted_battery_soc=adjusted_soc if hour == current_hour else float(row["battery_soc"]),
                note=note,
            )
        )

    return updated_schedule


def _build_explanation(
    action_type: str,
    deviation: float,
    battery_amount: float,
    gas_amount: float,
    market_amount: float,
    charge_amount: float,
    curtailment_amount: float,
    intraday_price: float | None,
) -> str:
    if deviation == 0:
        return "Actual demand matches the day-ahead plan for this hour, so no corrective action is needed."

    explanation_parts = []

    if deviation > 0:
        explanation_parts.append(
            f"Actual demand is higher than planned by {deviation:.2f}, so additional energy is required."
        )
        if battery_amount > 0:
            explanation_parts.append(
                f"The simulation first uses {battery_amount:.2f} from available battery discharge."
            )
        if gas_amount > 0:
            explanation_parts.append(
                f"It then uses {gas_amount:.2f} from gas generation."
            )
        if market_amount > 0:
            explanation_parts.append(
                f"The remaining {market_amount:.2f} is covered from the intraday market or grid."
            )
    else:
        explanation_parts.append(
            f"Actual demand is lower than planned by {abs(deviation):.2f}, so surplus energy must be absorbed."
        )
        if charge_amount > 0:
            explanation_parts.append(
                f"The simulation charges the battery with {charge_amount:.2f} first."
            )
        if curtailment_amount > 0:
            explanation_parts.append(
                f"The remaining {curtailment_amount:.2f} is marked for sell_to_market or curtailment."
            )

    if intraday_price is not None and intraday_price >= settings.HIGH_INTRADAY_PRICE_THRESHOLD:
        explanation_parts.append(
            "Intraday price is very high, so real-time market correction is expensive and should be minimized where possible."
        )

    explanation_parts.append(
        "This is a simple simulation-style correction for the current hour; remaining hours are kept explainable rather than fully re-optimized."
    )

    return " ".join(explanation_parts)
