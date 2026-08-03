from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.models import TripDirection


class AvailableSeatResponse(BaseModel):
    seat_id: int
    seat_number: str
    coach_id: int
    coach_number: int
    is_available: bool

class AvailabilityTripResponse(BaseModel):
    trip_id: int
    train_id: int
    train_number: str
    train_name: str
    direction: TripDirection
    departure_time: datetime
    arrival_time: datetime


class AvailabilityResponse(BaseModel):
    origin_station_id: int
    origin_station_name: str
    destination_station_id: int
    destination_station_name: str
    distance_km: Decimal
    estimated_fare: Decimal
    trip: AvailabilityTripResponse | None
    available_seats: list[AvailableSeatResponse]
    message: str