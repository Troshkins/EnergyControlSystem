from datetime import timedelta


def _validate_hourly_series(items, value_attr: str, label: str, allow_negative: bool = False):
    if len(items) != 24:
        raise ValueError(f"Expected 24 {label} values, got {len(items)}")

    timestamps = [item.timestamp for item in items]

    if len(set(timestamps)) != 24:
        raise ValueError(f"Duplicate timestamps found in {label}")

    sorted_timestamps = sorted(timestamps)
    for prev_ts, next_ts in zip(sorted_timestamps, sorted_timestamps[1:]):
        if next_ts - prev_ts != timedelta(hours=1):
            raise ValueError(f"{label} must be hourly and continuous")

    for item in items:
        value = getattr(item, value_attr)

        if value is None:
            raise ValueError(f"{label} contains missing values")

        if allow_negative:
            if value < -1000:
                raise ValueError(f"{label} has unrealistic negative values")
        else:
            if value < 0:
                raise ValueError(f"{label} cannot be negative")


def validate_prices(prices):
    _validate_hourly_series(prices, "price", "prices", allow_negative=True)


def validate_forecast(forecast):
    _validate_hourly_series(forecast, "demand", "forecast", allow_negative=False)


def validate_assets(data):
    if data.battery_capacity <= 0:
        raise ValueError("battery_capacity must be > 0")
    if data.max_charge <= 0:
        raise ValueError("max_charge must be > 0")
    if data.max_discharge <= 0:
        raise ValueError("max_discharge must be > 0")
    if data.gas_max_output <= 0:
        raise ValueError("gas_max_output must be > 0")
    if data.gas_cost < 0:
        raise ValueError("gas_cost cannot be negative")


def validate_intraday(data):
    if data.actual_demand < 0:
        raise ValueError("actual_demand cannot be negative")
