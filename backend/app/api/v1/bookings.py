from fastapi import APIRouter, status

from app.api.dependencies import DatabaseSession
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
)
from app.services.booking_service import (
    cancel_booking,
    create_booking,
    get_booking_by_reference,
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_booking(
    booking_data: BookingCreate,
    db: DatabaseSession,
) -> BookingResponse:
    return create_booking(
        db=db,
        booking_data=booking_data,
    )


@router.get(
    "/{booking_reference}",
    response_model=BookingResponse,
)
def get_booking(
    booking_reference: str,
    db: DatabaseSession,
) -> BookingResponse:
    return get_booking_by_reference(
        db=db,
        booking_reference=booking_reference,
    )


@router.post(
    "/{booking_reference}/cancel",
    response_model=BookingResponse,
)
def cancel_existing_booking(
    booking_reference: str,
    db: DatabaseSession,
) -> BookingResponse:
    return cancel_booking(
        db=db,
        booking_reference=booking_reference,
    )