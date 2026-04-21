def validate_prices(prices):
    if len(prices) != 24:
        raise ValueError(f"Expected 24 prices, got {len(prices)}")


def validate_forecast(forecast):
    if len(forecast) != 24:
        raise ValueError(f"Expected 24 forecast values, got {len(forecast)}")


def validate_assets(data):
    if data.battery_capacity <= 0:
        raise ValueError("Battery capacity must be > 0")


def validate_intraday(data):
    if data.actual_demand < 0:
        raise ValueError("Demand cannot be negative")
