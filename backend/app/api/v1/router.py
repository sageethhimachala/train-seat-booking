from fastapi import APIRouter

from app.api.v1 import (
    availability,
    bookings,
    stations,
    trips,
)


api_router = APIRouter()

api_router.include_router(stations.router)
api_router.include_router(trips.router)
api_router.include_router(availability.router)
api_router.include_router(bookings.router)