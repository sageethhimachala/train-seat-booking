from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.models import (
    BookingStatus,
    TripDirection,
)


class BookingCreate(BaseModel):
    trip_id: int = Field(gt=0)
    seat_id: int = Field(gt=0)
    origin_station_id: int = Field(gt=0)
    destination_station_id: int = Field(gt=0)

    passenger_name: str = Field(
        min_length=2,
        max_length=150,
    )

    passenger_email: EmailStr | None = None


class BookingSeatResponse(BaseModel):
    id: int
    seat_number: str
    coach_number: int


class BookingStationResponse(BaseModel):
    id: int
    name: str
    code: str


class BookingTripResponse(BaseModel):
    id: int
    train_id: int
    train_number: str
    train_name: str
    direction: TripDirection
    departure_time: datetime
    arrival_time: datetime


class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    passenger_name: str
    passenger_email: str | None
    fare: Decimal
    status: BookingStatus
    created_at: datetime
    cancelled_at: datetime | None

    trip: BookingTripResponse
    seat: BookingSeatResponse
    origin_station: BookingStationResponse
    destination_station: BookingStationResponse

    model_config = ConfigDict(from_attributes=True)