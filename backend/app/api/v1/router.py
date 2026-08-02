from fastapi import APIRouter

from app.api.v1 import (
    availability,
    stations,
    trips,
)


api_router = APIRouter()

api_router.include_router(stations.router)
api_router.include_router(trips.router)
api_router.include_router(availability.router)