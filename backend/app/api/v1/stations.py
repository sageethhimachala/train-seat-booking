from fastapi import APIRouter
from sqlalchemy import select

from app.api.dependencies import DatabaseSession
from app.models.models import Station
from app.schemas.station import StationResponse


router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
)


@router.get(
    "",
    response_model=list[StationResponse],
)
def get_stations(
    db: DatabaseSession,
) -> list[Station]:
    statement = (
        select(Station)
        .order_by(Station.order_index)
    )

    stations = db.scalars(statement).all()

    return stations