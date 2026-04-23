from app.producers.kafka_producer import kafka_producer
from app.repositories.assets_repo import save_assets
from app.repositories.forecast_repo import save_forecast
from app.repositories.intraday_repo import save_intraday
from app.repositories.prices_repo import save_prices
from app.services.validation_service import (
    validate_assets,
    validate_forecast,
    validate_intraday,
    validate_prices,
)


def _dump(item):
    return item.model_dump() if hasattr(item, "model_dump") else item.dict()


def ingest_prices(db, data):
    validate_prices(data.prices)
    save_prices(db, data.prices)

    kafka_producer.send(
        topic="price_signals",
        message={"prices": [_dump(item) for item in data.prices]},
        key="prices",
    )

    return {"status": "prices stored and published to Kafka"}


def ingest_forecast(db, data):
    validate_forecast(data.forecast)
    save_forecast(db, data.forecast)

    kafka_producer.send(
        topic="demand_forecasts",
        message={"forecast": [_dump(item) for item in data.forecast]},
        key="forecast",
    )

    return {"status": "forecast stored and published to Kafka"}


def ingest_assets(db, data):
    validate_assets(data)
    save_assets(db, data)

    return {"status": "assets stored"}


def ingest_intraday(db, data):
    validate_intraday(data)
    save_intraday(db, data)

    kafka_producer.send(
        topic="intraday_updates",
        message=_dump(data),
        key="intraday",
    )

    return {"status": "intraday update stored and published to Kafka"}
