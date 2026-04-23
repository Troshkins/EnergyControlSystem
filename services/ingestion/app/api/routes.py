from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.producers.kafka_producer import kafka_producer
from app.schemas.energy import (
    AssetsInput,
    ForecastInput,
    IntradayInput,
    PriceInput,
)
from app.services.ingestion_service import (
    ingest_assets,
    ingest_forecast,
    ingest_intraday,
    ingest_prices,
)

router = APIRouter()


@router.get("/")
def root():
    return {"message": "ECS Ingestion Service is running"}


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")

    kafka_ok = kafka_producer.healthcheck()

    return {
        "status": "ok",
        "database": "connected",
        "kafka": "connected" if kafka_ok else "disconnected",
    }


@router.post("/prices")
def upload_prices(data: PriceInput, db: Session = Depends(get_db)):
    try:
        return ingest_prices(db, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/forecast")
def upload_forecast(data: ForecastInput, db: Session = Depends(get_db)):
    try:
        return ingest_forecast(db, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/assets")
def upload_assets(data: AssetsInput, db: Session = Depends(get_db)):
    try:
        return ingest_assets(db, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/intraday")
def upload_intraday(data: IntradayInput, db: Session = Depends(get_db)):
    try:
        return ingest_intraday(db, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
