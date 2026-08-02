from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.models import TripDirection, TripStatus
from app.schemas.station import StationResponse


class TrainSummary(BaseModel):
    id: int
    train_number: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class TripResponse(BaseModel):
    id: int
    departure_time: datetime
    arrival_time: datetime
    direction: TripDirection
    status: TripStatus
    train: TrainSummary
    start_station: StationResponse
    end_station: StationResponse

    model_config = ConfigDict(from_attributes=True)