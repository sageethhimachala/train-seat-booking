import secrets
import string
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.models import (
    Booking,
    BookingStatus,
    Coach,
    CoachType,
    Seat,
    Station,
    Trip,
    TripDirection,
    TripStatus,
)
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingSeatResponse,
    BookingStationResponse,
    BookingTripResponse,
)


FARE_PER_KM = Decimal("3.00")


def generate_booking_reference() -> str:
    alphabet = string.ascii_uppercase + string.digits

    random_part = "".join(
        secrets.choice(alphabet)
        for _ in range(8)
    )

    return f"TRN-{random_part}"


def get_station_or_404(
    db: Session,
    station_id: int,
) -> Station:
    station = db.get(Station, station_id)

    if station is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station {station_id} was not found.",
        )

    return station


def determine_direction(
    origin: Station,
    destination: Station,
) -> TripDirection:
    if origin.id == destination.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Origin and destination stations "
                "must be different."
            ),
        )

    if origin.order_index < destination.order_index:
        return TripDirection.FORWARD

    return TripDirection.REVERSE


def calculate_fare(
    origin: Station,
    destination: Station,
) -> Decimal:
    distance = abs(
        origin.distance_from_start_km
        - destination.distance_from_start_km
    )

    return (
        distance * FARE_PER_KM
    ).quantize(Decimal("0.01"))


def validate_trip_is_bookable(
    trip: Trip,
) -> None:
    now = datetime.now(timezone.utc)

    if trip.status not in {
        TripStatus.SCHEDULED,
        TripStatus.BOARDING,
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Bookings are not allowed for this "
                f"trip because its status is {trip.status.value}."
            ),
        )

    if trip.departure_time <= now:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Bookings are closed because the train "
                "has already left its starting station."
            ),
        )


def validate_requested_leg(
    trip: Trip,
    origin: Station,
    destination: Station,
) -> None:
    requested_direction = determine_direction(
        origin,
        destination,
    )

    if requested_direction != trip.direction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The selected origin and destination "
                "do not follow the trip direction."
            ),
        )

    trip_start_index = trip.start_station.order_index
    trip_end_index = trip.end_station.order_index

    trip_low = min(
        trip_start_index,
        trip_end_index,
    )

    trip_high = max(
        trip_start_index,
        trip_end_index,
    )

    requested_low = min(
        origin.order_index,
        destination.order_index,
    )

    requested_high = max(
        origin.order_index,
        destination.order_index,
    )

    if not (
        trip_low <= requested_low
        and requested_high <= trip_high
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The selected trip does not cover the "
                "requested origin and destination."
            ),
        )


def lock_and_get_seat(
    db: Session,
    seat_id: int,
) -> Seat:
    statement = (
        select(Seat)
        .where(Seat.id == seat_id)
        .with_for_update(of=Seat)
    )

    seat = db.scalar(statement)

    if seat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seat {seat_id} was not found.",
        )

    # Accessing this relationship runs a separate SELECT.
    # It does not interfere with the seat row lock.
    _ = seat.coach

    return seat


def validate_seat_for_trip(
    seat: Seat,
    trip: Trip,
) -> None:
    if seat.coach.train_id != trip.train_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The selected seat does not belong "
                "to this trip's train."
            ),
        )

    if seat.coach.coach_type != CoachType.RESERVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only seats in reserved coaches "
                "can be booked."
            ),
        )


def has_overlapping_booking(
    db: Session,
    trip_id: int,
    seat_id: int,
    origin: Station,
    destination: Station,
) -> bool:
    requested_start = min(
        origin.order_index,
        destination.order_index,
    )

    requested_end = max(
        origin.order_index,
        destination.order_index,
    )

    existing_origin = Station.__table__.alias(
        "existing_origin"
    )

    existing_destination = Station.__table__.alias(
        "existing_destination"
    )

    existing_start = func.least(
        existing_origin.c.order_index,
        existing_destination.c.order_index,
    )

    existing_end = func.greatest(
        existing_origin.c.order_index,
        existing_destination.c.order_index,
    )

    statement = (
        select(Booking.id)
        .join(
            existing_origin,
            Booking.origin_station_id
            == existing_origin.c.id,
        )
        .join(
            existing_destination,
            Booking.destination_station_id
            == existing_destination.c.id,
        )
        .where(
            Booking.trip_id == trip_id,
            Booking.seat_id == seat_id,
            Booking.status == BookingStatus.CONFIRMED,
            existing_start < requested_end,
            existing_end > requested_start,
        )
        .limit(1)
    )

    return db.scalar(statement) is not None


def generate_unique_booking_reference(
    db: Session,
) -> str:
    for _ in range(10):
        reference = generate_booking_reference()

        existing_reference = db.scalar(
            select(Booking.id).where(
                Booking.booking_reference == reference
            )
        )

        if existing_reference is None:
            return reference

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a booking reference.",
    )


def get_booking_statement(
    booking_reference: str,
):
    return (
        select(Booking)
        .options(
            joinedload(Booking.trip)
            .joinedload(Trip.train),
            joinedload(Booking.trip)
            .joinedload(Trip.start_station),
            joinedload(Booking.trip)
            .joinedload(Trip.end_station),
            joinedload(Booking.seat)
            .joinedload(Seat.coach),
            joinedload(Booking.origin_station),
            joinedload(Booking.destination_station),
        )
        .where(
            Booking.booking_reference
            == booking_reference
        )
    )


def build_booking_response(
    booking: Booking,
) -> BookingResponse:
    return BookingResponse(
        id=booking.id,
        booking_reference=booking.booking_reference,
        passenger_name=booking.passenger_name,
        passenger_email=booking.passenger_email,
        fare=booking.fare,
        status=booking.status,
        created_at=booking.created_at,
        cancelled_at=booking.cancelled_at,
        trip=BookingTripResponse(
            id=booking.trip.id,
            train_id=booking.trip.train.id,
            train_number=(
                booking.trip.train.train_number
            ),
            train_name=booking.trip.train.name,
            direction=booking.trip.direction,
            departure_time=(
                booking.trip.departure_time
            ),
            arrival_time=booking.trip.arrival_time,
        ),
        seat=BookingSeatResponse(
            id=booking.seat.id,
            seat_number=booking.seat.seat_number,
            coach_number=(
                booking.seat.coach.coach_number
            ),
        ),
        origin_station=BookingStationResponse(
            id=booking.origin_station.id,
            name=booking.origin_station.name,
            code=booking.origin_station.code,
        ),
        destination_station=BookingStationResponse(
            id=booking.destination_station.id,
            name=booking.destination_station.name,
            code=booking.destination_station.code,
        ),
    )


def create_booking(
    db: Session,
    booking_data: BookingCreate,
) -> BookingResponse:
    try:
        trip_statement = (
            select(Trip)
            .options(
                joinedload(Trip.train),
                joinedload(Trip.start_station),
                joinedload(Trip.end_station),
            )
            .where(Trip.id == booking_data.trip_id)
        )

        trip = db.scalar(trip_statement)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Trip {booking_data.trip_id} "
                    "was not found."
                ),
            )

        validate_trip_is_bookable(trip)

        origin = get_station_or_404(
            db,
            booking_data.origin_station_id,
        )

        destination = get_station_or_404(
            db,
            booking_data.destination_station_id,
        )

        validate_requested_leg(
            trip,
            origin,
            destination,
        )

        # PostgreSQL row lock.
        #
        # Two requests attempting to book the same
        # physical seat must acquire this lock one
        # after the other.
        seat = lock_and_get_seat(
            db,
            booking_data.seat_id,
        )

        validate_seat_for_trip(
            seat,
            trip,
        )

        # Recheck after obtaining the seat lock.
        #
        # The first concurrent request may have created
        # a booking while the second request was waiting.
        if has_overlapping_booking(
            db=db,
            trip_id=trip.id,
            seat_id=seat.id,
            origin=origin,
            destination=destination,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The selected seat is no longer "
                    "available for this journey segment."
                ),
            )

        booking = Booking(
            booking_reference=(
                generate_unique_booking_reference(db)
            ),
            trip_id=trip.id,
            seat_id=seat.id,
            origin_station_id=origin.id,
            destination_station_id=destination.id,
            passenger_name=(
                booking_data.passenger_name.strip()
            ),
            passenger_email=(
                str(booking_data.passenger_email)
                if booking_data.passenger_email
                else None
            ),
            fare=calculate_fare(
                origin,
                destination,
            ),
            status=BookingStatus.CONFIRMED,
        )

        db.add(booking)
        db.commit()

        saved_booking = db.scalar(
            get_booking_statement(
                booking.booking_reference
            )
        )

        if saved_booking is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail="Booking was created but could not be loaded.",
            )

        return build_booking_response(saved_booking)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


def get_booking_by_reference(
    db: Session,
    booking_reference: str,
) -> BookingResponse:
    normalized_reference = (
        booking_reference.strip().upper()
    )

    booking = db.scalar(
        get_booking_statement(
            normalized_reference
        )
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Booking {normalized_reference} "
                "was not found."
            ),
        )

    return build_booking_response(booking)


def cancel_booking(
    db: Session,
    booking_reference: str,
) -> BookingResponse:
    normalized_reference = (
        booking_reference.strip().upper()
    )

    try:
        lock_statement = (
            select(Booking)
            .where(
                Booking.booking_reference
                == normalized_reference
            )
            .with_for_update()
        )

        booking = db.scalar(lock_statement)

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Booking {normalized_reference} "
                    "was not found."
                ),
            )

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The booking is already cancelled.",
            )

        trip = db.get(Trip, booking.trip_id)

        if trip is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "The trip associated with this "
                    "booking could not be found."
                ),
            )

        now = datetime.now(timezone.utc)

        if (
            trip.status
            not in {
                TripStatus.SCHEDULED,
                TripStatus.BOARDING,
            }
            or trip.departure_time <= now
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This booking cannot be cancelled "
                    "after the train leaves its "
                    "starting station."
                ),
            )

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = now

        db.commit()

        cancelled_booking = db.scalar(
            get_booking_statement(
                normalized_reference
            )
        )

        if cancelled_booking is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "The cancelled booking could not "
                    "be loaded."
                ),
            )

        return build_booking_response(
            cancelled_booking
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise