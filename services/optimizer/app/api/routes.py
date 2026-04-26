import logging
from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.producers.kafka_producer import kafka_producer
from app.repositories.schedule_repo import (
    get_latest_schedule_run_by_date,
    get_schedule_runs_by_date,
    save_day_ahead_schedule,
)
from app.schemas.optimization import (
    DayAheadOptimizationRequest,
    DayAheadOptimizationResponse,
    ScheduleLookupResponse,
)
from app.services.day_ahead_optimizer import optimize_day_ahead

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def root():
    return {"message": "ECS Optimization Service is running"}


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


@router.post("/optimize/day-ahead", response_model=DayAheadOptimizationResponse)
def optimize_day_ahead_route(
    request: DayAheadOptimizationRequest,
    db: Session = Depends(get_db),
):
    try:
        optimization_response = optimize_day_ahead(request)
        run_id = uuid4()
        optimization_response.run_id = run_id
        save_day_ahead_schedule(db, run_id, optimization_response)
        try:
            kafka_producer.send(
                topic=settings.KAFKA_SCHEDULE_TOPIC,
                message=optimization_response.model_dump(mode="json"),
                key=str(run_id),
            )
        except Exception:
            logger.exception("Schedule persistence succeeded but Kafka publish failed")
        return optimization_response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist day-ahead schedule: {exc}",
        )


@router.get("/schedule/{schedule_date}", response_model=ScheduleLookupResponse)
def get_schedule_by_date(
    schedule_date: date,
    all_runs: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        if all_runs:
            runs = get_schedule_runs_by_date(db, schedule_date)
            if not runs:
                raise HTTPException(
                    status_code=404,
                    detail=f"No day-ahead schedule found for {schedule_date.isoformat()}.",
                )
            return ScheduleLookupResponse(
                date=schedule_date,
                status="ok",
                runs=runs,
            )

        run = get_latest_schedule_run_by_date(db, schedule_date)
        if run is None:
            raise HTTPException(
                status_code=404,
                detail=f"No day-ahead schedule found for {schedule_date.isoformat()}.",
            )

        return ScheduleLookupResponse(
            date=schedule_date,
            status="ok",
            run=run,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load day-ahead schedule: {exc}",
        )
