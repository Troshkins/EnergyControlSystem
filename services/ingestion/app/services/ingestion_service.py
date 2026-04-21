from app.repositories.prices_repo import save_prices
from app.repositories.forecast_repo import save_forecast
from app.repositories.assets_repo import save_assets
from app.repositories.intraday_repo import save_intraday

from app.services.validation_service import (
    validate_prices,
    validate_forecast,
    validate_assets,
    validate_intraday,
)

from app.producers.kafka_producer import kafka_producer


def ingest_prices(db, data):
    validate_prices(data.prices)
    save_prices(db, data.prices)

    kafka_producer.send(
        topic="price_signals",
        message={"prices": [p.dict() for p in data.prices]},
        key="prices",
    )

    return {"status": "prices stored and published to Kafka"}


def ingest_forecast(db, data):
    validate_forecast(data.forecast)
    save_forecast(db, data.forecast)

    kafka_producer.send(
        topic="demand_forecasts",
        message={"forecast": [f.dict() for f in data.forecast]},
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
        message=data.dict(),
        key="intraday",
    )

    return {"status": "intraday update stored and published to Kafka"}
