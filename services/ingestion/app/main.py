from app.core.database import Base, engine
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="ECS Ingestion Service",
    version="0.1.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ingestion",
        "environment": settings.APP_ENV
    }
