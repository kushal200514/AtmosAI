from fastapi import FastAPI

from app.config import settings

from app.routes import (
    forecast,
    locations,
    profiles,
    accuracy,
    alerts,
    telemetry,
)


app = FastAPI(
    title="AtmosAI Backend",
    description="AI-powered air pollution early warning system",
    version="1.0.0",
)


@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "service": "AtmosAI Backend",
        "environment": settings.environment,
        "dynamodb": settings.use_dynamodb
    }


app.include_router(
    forecast.router,
    prefix="/api"
)

app.include_router(
    locations.router,
    prefix="/api"
)

app.include_router(
    profiles.router,
    prefix="/api"
)

app.include_router(
    accuracy.router,
    prefix="/api"
)

app.include_router(
    alerts.router,
    prefix="/api"
)

app.include_router(
    telemetry.router,
    prefix="/api",
)