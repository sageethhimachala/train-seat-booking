from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import DatabaseSession
from app.schemas.availability import AvailabilityResponse
from app.services.availability_service import (
    search_availability,
)


router = APIRouter(
    prefix="/availability",
    tags=["Availability"],
)


@router.get(
    "",
    response_model=AvailabilityResponse,
)
def get_availability(
    db: DatabaseSession,
    origin_station_id: Annotated[
        int,
        Query(gt=0),
    ],
    destination_station_id: Annotated[
        int,
        Query(gt=0),
    ],
) -> AvailabilityResponse:
    return search_availability(
        db=db,
        origin_station_id=origin_station_id,
        destination_station_id=destination_station_id,
    )