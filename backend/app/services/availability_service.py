from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.models import (
    Booking,
    BookingStatus,
    Coach,
    CoachType,
    Seat,
    Station,
    Train,
    Trip,
    TripDirection,
    TripStatus,
)
from app.schemas.availability import (
    AvailabilityResponse,
    AvailabilityTripResponse,
    AvailableSeatResponse,
)


FARE_PER_KM = Decimal("3.00")


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
    if origin.order_index == destination.order_index:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Origin and destination stations must be different."
            ),
        )

    if origin.order_index < destination.order_index:
        return TripDirection.FORWARD

    return TripDirection.REVERSE


def calculate_distance(
    origin: Station,
    destination: Station,
) -> Decimal:
    return abs(
        origin.distance_from_start_km - destination.distance_from_start_km
    )


def calculate_fare(distance_km: Decimal) -> Decimal:
    fare = distance_km * FARE_PER_KM

    return fare.quantize(Decimal("0.01"))


def get_upcoming_matching_trips(
    db: Session,
    direction: TripDirection,
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
            Trip.direction == direction,
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

    return db.scalars(statement).all()


def trip_covers_requested_leg(
    trip: Trip,
    origin: Station,
    destination: Station,
) -> bool:
    trip_start = trip.start_station.order_index
    trip_end = trip.end_station.order_index

    trip_low = min(trip_start, trip_end)
    trip_high = max(trip_start, trip_end)

    requested_low = min(
        origin.order_index,
        destination.order_index,
    )

    requested_high = max(
        origin.order_index,
        destination.order_index,
    )

    return (
        trip_low <= requested_low
        and requested_high <= trip_high
    )


def get_available_seats_for_trip(
    db: Session,
    trip: Trip,
    origin: Station,
    destination: Station,
) -> list[AvailableSeatResponse]:

    requested_start = min(
        origin.order_index,
        destination.order_index,
    )

    requested_end = max(
        origin.order_index,
        destination.order_index,
    )

    # Consider as SQL statement

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

    overlapping_booking_exists = exists(
        select(Booking.id)
        .join(
            existing_origin,
            Booking.origin_station_id == existing_origin.c.id,
        )
        .join(
            existing_destination,
            Booking.destination_station_id == existing_destination.c.id,
        )
        .where(
            Booking.trip_id == trip.id,
            Booking.seat_id == Seat.id,
            Booking.status == BookingStatus.CONFIRMED,
            existing_start < requested_end,
            existing_end > requested_start,
        )
    )

    statement = (
        select(
            Seat.id,
            Seat.seat_number,
            Coach.id,
            Coach.coach_number,
        )
        .join(Coach, Seat.coach_id == Coach.id)
        .where(
            Coach.train_id == trip.train_id,
            Coach.coach_type == CoachType.RESERVED,
            ~overlapping_booking_exists,
        )
        .order_by(
            Coach.coach_number,
            Seat.seat_number,
        )
    )

    rows = db.execute(statement).all()

    return [
        AvailableSeatResponse(
            seat_id=seat_id,
            seat_number=seat_number,
            coach_id=coach_id,
            coach_number=coach_number,
        )
        for (
            seat_id,
            seat_number,
            coach_id,
            coach_number,
        ) in rows
    ]


def search_availability(
    db: Session,
    origin_station_id: int,
    destination_station_id: int,
) -> AvailabilityResponse:
    origin = get_station_or_404(
        db,
        origin_station_id,
    )

    destination = get_station_or_404(
        db,
        destination_station_id,
    )

    direction = determine_direction(
        origin,
        destination,
    )

    distance_km = calculate_distance(
        origin,
        destination,
    )

    estimated_fare = calculate_fare(distance_km)

    trips = get_upcoming_matching_trips(
        db,
        direction,
    )

    for trip in trips:
        if not trip_covers_requested_leg(
            trip,
            origin,
            destination,
        ):
            continue

        available_seats = get_available_seats_for_trip(
            db,
            trip,
            origin,
            destination,
        )

        if available_seats:
            return AvailabilityResponse(
                origin_station_id=origin.id,
                origin_station_name=origin.name,
                destination_station_id=destination.id,
                destination_station_name=destination.name,
                distance_km=distance_km,
                estimated_fare=estimated_fare,
                trip=AvailabilityTripResponse(
                    trip_id=trip.id,
                    train_id=trip.train.id,
                    train_number=trip.train.train_number,
                    train_name=trip.train.name,
                    direction=trip.direction,
                    departure_time=trip.departure_time,
                    arrival_time=trip.arrival_time,
                ),
                available_seats=available_seats,
                message=(
                    f"{len(available_seats)} Available seats found on the earliest eligible train."
                ),
            )

    if not trips:
        message = (
            "No upcoming train is currently available at the starting terminal for this direction."
        )
    else:
        message = (
            "No reserved seats are available on any upcoming eligible train."
        )

    return AvailabilityResponse(
        origin_station_id=origin.id,
        origin_station_name=origin.name,
        destination_station_id=destination.id,
        destination_station_name=destination.name,
        distance_km=distance_km,
        estimated_fare=estimated_fare,
        trip=None,
        available_seats=[],
        message=message,
    )