from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.producers.kafka_producer import kafka_producer
from app.repositories.intraday_repo import get_intraday_actions_by_date
from app.schemas.intraday import (
    IntradayActionListResponse,
    IntradayOptimizationRequest,
    IntradayOptimizationResponse,
)
from app.services.intraday_optimizer import optimize_intraday_update

router = APIRouter()


@router.get("/")
def root():
    return {"message": "ECS Intraday Service is running"}


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


@router.post("/optimize/intraday", response_model=IntradayOptimizationResponse)
def optimize_intraday_route(
    request: IntradayOptimizationRequest,
    db: Session = Depends(get_db),
):
    try:
        return optimize_intraday_update(request, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process intraday update: {exc}",
        )


@router.get("/intraday/actions/{action_date}", response_model=IntradayActionListResponse)
def get_intraday_actions_route(
    action_date: date,
    db: Session = Depends(get_db),
):
    try:
        actions = get_intraday_actions_by_date(db, action_date)
        return IntradayActionListResponse(
            date=action_date,
            actions=actions,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load intraday actions: {exc}",
        )
