from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.energy import (
    PriceInput,
    ForecastInput,
    AssetsInput,
    IntradayInput,
)
from app.services.ingestion_service import (
    ingest_prices,
    ingest_forecast,
    ingest_assets,
    ingest_intraday,
)

router = APIRouter()


@router.post("/prices")
def upload_prices(data: PriceInput, db: Session = Depends(get_db)):
    try:
        return ingest_prices(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forecast")
def upload_forecast(data: ForecastInput, db: Session = Depends(get_db)):
    try:
        return ingest_forecast(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assets")
def upload_assets(data: AssetsInput, db: Session = Depends(get_db)):
    try:
        return ingest_assets(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/intraday")
def upload_intraday(data: IntradayInput, db: Session = Depends(get_db)):
    try:
        return ingest_intraday(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def root():
    return {"message": "ECS Ingestion Service is running"}
