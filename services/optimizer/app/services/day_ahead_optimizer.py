from datetime import timedelta

from ortools.linear_solver import pywraplp

from app.schemas.optimization import (
    AssetConstraints,
    DayAheadOptimizationRequest,
    DayAheadOptimizationResponse,
    DemandPoint,
    PricePoint,
    ScheduleHour,
)


HORIZON_HOURS = 24
ROUNDING_DECIMALS = 6
OPTIMAL_STATUSES = {
    pywraplp.Solver.OPTIMAL,
    pywraplp.Solver.FEASIBLE,
}
SOLVER_STATUS_NAMES = {
    pywraplp.Solver.OPTIMAL: "OPTIMAL",
    pywraplp.Solver.FEASIBLE: "FEASIBLE",
    pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
    pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
    pywraplp.Solver.ABNORMAL: "ABNORMAL",
    pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
}


def _round_output_value(value: float) -> float:
    rounded = round(value, ROUNDING_DECIMALS)
    if rounded == -0.0:
        return 0.0
    return rounded


def _validate_asset_constraints(asset_constraints: AssetConstraints):
    numeric_constraints = {
        "battery_capacity": asset_constraints.battery_capacity,
        "max_charge": asset_constraints.max_charge,
        "max_discharge": asset_constraints.max_discharge,
        "gas_max_output": asset_constraints.gas_max_output,
        "initial_battery_soc": asset_constraints.initial_battery_soc,
    }

    for name, value in numeric_constraints.items():
        if value < 0:
            raise ValueError(f"{name} must be greater than or equal to 0.")

    if asset_constraints.initial_battery_soc > asset_constraints.battery_capacity:
        raise ValueError("initial_battery_soc cannot exceed battery_capacity.")


def _sort_and_validate_points(
    prices: list[PricePoint],
    demand_forecast: list[DemandPoint],
):
    if len(prices) != HORIZON_HOURS:
        raise ValueError("Expected exactly 24 price points.")

    if len(demand_forecast) != HORIZON_HOURS:
        raise ValueError("Expected exactly 24 demand forecast points.")

    sorted_prices = sorted(prices, key=lambda point: point.timestamp)
    sorted_demand = sorted(demand_forecast, key=lambda point: point.timestamp)

    price_timestamps = [point.timestamp for point in sorted_prices]
    demand_timestamps = [point.timestamp for point in sorted_demand]

    if len(set(price_timestamps)) != HORIZON_HOURS:
        raise ValueError("Price points must contain 24 unique timestamps.")

    if len(set(demand_timestamps)) != HORIZON_HOURS:
        raise ValueError("Demand forecast must contain 24 unique timestamps.")

    for index in range(1, HORIZON_HOURS):
        expected_price_timestamp = price_timestamps[index - 1] + timedelta(hours=1)
        expected_demand_timestamp = demand_timestamps[index - 1] + timedelta(hours=1)

        if price_timestamps[index] != expected_price_timestamp:
            raise ValueError("Price timestamps must form a continuous 24-hour horizon.")

        if demand_timestamps[index] != expected_demand_timestamp:
            raise ValueError("Demand timestamps must form a continuous 24-hour horizon.")

    if price_timestamps != demand_timestamps:
        raise ValueError(
            "Price and demand forecast timestamps must match for all 24 hours."
        )

    return sorted_prices, sorted_demand


def optimize_day_ahead(
    request: DayAheadOptimizationRequest,
) -> DayAheadOptimizationResponse:
    _validate_asset_constraints(request.asset_constraints)
    prices, demand_forecast = _sort_and_validate_points(
        request.prices,
        request.demand_forecast,
    )

    solver = pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise ValueError("Failed to initialize OR-Tools CBC solver.")

    infinity = solver.infinity()
    constraints = request.asset_constraints

    grid_usage = [
        solver.NumVar(0.0, infinity, f"grid_usage_{hour}")
        for hour in range(HORIZON_HOURS)
    ]
    gas_usage = [
        solver.NumVar(0.0, constraints.gas_max_output, f"gas_usage_{hour}")
        for hour in range(HORIZON_HOURS)
    ]
    battery_charge = [
        solver.NumVar(0.0, constraints.max_charge, f"battery_charge_{hour}")
        for hour in range(HORIZON_HOURS)
    ]
    battery_discharge = [
        solver.NumVar(0.0, constraints.max_discharge, f"battery_discharge_{hour}")
        for hour in range(HORIZON_HOURS)
    ]
    battery_soc = [
        solver.NumVar(0.0, constraints.battery_capacity, f"battery_soc_{hour}")
        for hour in range(HORIZON_HOURS)
    ]
    is_charging = [
        solver.BoolVar(f"is_charging_{hour}") for hour in range(HORIZON_HOURS)
    ]
    is_discharging = [
        solver.BoolVar(f"is_discharging_{hour}") for hour in range(HORIZON_HOURS)
    ]

    for hour in range(HORIZON_HOURS):
        demand_value = demand_forecast[hour].demand

        solver.Add(
            grid_usage[hour]
            + gas_usage[hour]
            + battery_discharge[hour]
            == demand_value + battery_charge[hour]
        )

        previous_soc = (
            constraints.initial_battery_soc
            if hour == 0
            else battery_soc[hour - 1]
        )
        solver.Add(
            battery_soc[hour]
            == previous_soc + battery_charge[hour] - battery_discharge[hour]
        )
        solver.Add(gas_usage[hour] <= constraints.gas_max_output)
        solver.Add(
            battery_charge[hour] <= constraints.max_charge * is_charging[hour]
        )
        solver.Add(
            battery_discharge[hour]
            <= constraints.max_discharge * is_discharging[hour]
        )
        solver.Add(is_charging[hour] + is_discharging[hour] <= 1)

    objective = solver.Objective()
    for hour in range(HORIZON_HOURS):
        objective.SetCoefficient(grid_usage[hour], prices[hour].price)
        objective.SetCoefficient(gas_usage[hour], constraints.gas_cost)
    objective.SetMinimization()

    result_status = solver.Solve()
    if result_status not in OPTIMAL_STATUSES:
        status_name = SOLVER_STATUS_NAMES.get(result_status, str(result_status))
        raise ValueError(
            "Day-ahead optimization model is infeasible or could not be solved. "
            f"Solver status: {status_name}."
        )

    schedule = []
    total_cost = 0.0

    for hour in range(HORIZON_HOURS):
        grid_value = _round_output_value(grid_usage[hour].solution_value())
        gas_value = _round_output_value(gas_usage[hour].solution_value())
        charge_value = _round_output_value(battery_charge[hour].solution_value())
        discharge_value = _round_output_value(
            battery_discharge[hour].solution_value()
        )
        soc_value = _round_output_value(battery_soc[hour].solution_value())
        price_value = _round_output_value(prices[hour].price)
        demand_value = _round_output_value(demand_forecast[hour].demand)
        hour_cost = _round_output_value(
            (grid_value * price_value) + (gas_value * constraints.gas_cost)
        )

        total_cost += hour_cost
        schedule.append(
            ScheduleHour(
                timestamp=prices[hour].timestamp,
                hour=hour,
                price=price_value,
                demand=demand_value,
                grid_usage=grid_value,
                gas_usage=gas_value,
                battery_charge=charge_value,
                battery_discharge=discharge_value,
                battery_soc=soc_value,
                hour_cost=hour_cost,
            )
        )

    return DayAheadOptimizationResponse(
        status="optimal" if result_status == pywraplp.Solver.OPTIMAL else "feasible",
        explanation=(
            "Computed a 24-hour day-ahead schedule that minimizes grid and gas cost "
            "while meeting demand and respecting battery and gas asset constraints."
        ),
        total_cost=_round_output_value(total_cost),
        schedule=schedule,
    )


class DayAheadOptimizer:
    def optimize(
        self,
        request: DayAheadOptimizationRequest,
    ) -> DayAheadOptimizationResponse:
        return optimize_day_ahead(request)


day_ahead_optimizer = DayAheadOptimizer()
