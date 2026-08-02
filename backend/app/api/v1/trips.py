from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.dependencies import DatabaseSession
from app.models.models import (
    Train,
    Trip,
    TripStatus,
)
from app.schemas.trip import TripResponse


router = APIRouter(
    prefix="/trips",
    tags=["Trips"],
)


@router.get(
    "/upcoming",
    response_model=list[TripResponse],
)
def get_upcoming_trips(
    db: DatabaseSession,
) -> list[Trip]:
    now = datetime.now(timezone.utc)

    statement = (
        select(Trip)
        .join(Trip.train)
        .options(
            joinedload(Trip.train),
            joinedload(Trip.start_station),
            joinedload(Trip.end_station),
        )
        .where(
            Trip.departure_time > now,
            Trip.status.in_(
                [
                    TripStatus.SCHEDULED,
                    TripStatus.BOARDING,
                ]
            ),
            Train.is_active.is_(True),
        )
        .order_by(Trip.departure_time)
    )

    trips = db.scalars(statement).all()

    return trips