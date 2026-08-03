from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.scheduler import (
    start_trip_scheduler,
    stop_trip_scheduler,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    start_trip_scheduler()

    yield

    stop_trip_scheduler()


app = FastAPI(
    title="Segment-Based Train Seat Booking API",
    description=(
        "API for booking reserved train seats across "
        "non-overlapping railway journey segments."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": "Train Seat Booking API is running"
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy"
    }