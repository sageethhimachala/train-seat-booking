from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (
    Trip,
    TripDirection,
    TripStatus,
)

from app.services.trip_scheduler_service import (
    ensure_scheduled_trip_for_active_trains,
    update_boarding_trips,
    update_completed_trips,
    update_departed_trips,
)


def test_scheduled_trip_enters_boarding(
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]

    now = datetime.now(timezone.utc)

    trip.departure_time = (
        now + timedelta(minutes=10)
    )

    trip.arrival_time = (
        now + timedelta(hours=10)
    )

    db.commit()

    count = update_boarding_trips(
        db,
        now,
    )

    db.commit()
    db.refresh(trip)

    assert count == 1
    assert trip.status == TripStatus.BOARDING


def test_boarding_creates_reverse_trip(
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]
    train = seeded_data["train"]

    now = datetime.now(timezone.utc)

    trip.departure_time = (
        now + timedelta(minutes=10)
    )

    trip.arrival_time = (
        now + timedelta(hours=10)
    )

    db.commit()

    update_boarding_trips(
        db,
        now,
    )

    db.commit()

    next_trip = db.scalar(
        select(Trip)
        .where(
            Trip.train_id == train.id,
            Trip.status == TripStatus.SCHEDULED,
        )
    )

    assert next_trip is not None

    assert (
        next_trip.direction
        == TripDirection.REVERSE
    )

    assert (
        next_trip.start_station_id
        == trip.end_station_id
    )

    assert (
        next_trip.end_station_id
        == trip.start_station_id
    )


def test_boarding_trip_becomes_departed(
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]

    now = datetime.now(timezone.utc)

    trip.status = TripStatus.BOARDING
    trip.departure_time = (
        now - timedelta(minutes=1)
    )
    trip.arrival_time = (
        now + timedelta(hours=10)
    )

    db.commit()

    count = update_departed_trips(
        db,
        now,
    )

    db.commit()
    db.refresh(trip)

    assert count == 1
    assert trip.status == TripStatus.DEPARTED


def test_departed_trip_becomes_completed(
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]

    now = datetime.now(timezone.utc)

    trip.status = TripStatus.DEPARTED

    trip.departure_time = (
        now - timedelta(hours=10)
    )

    trip.arrival_time = (
        now - timedelta(minutes=1)
    )

    db.commit()

    count = update_completed_trips(
        db,
        now,
    )

    db.commit()
    db.refresh(trip)

    assert count == 1
    assert trip.status == TripStatus.COMPLETED


def test_future_trip_remains_scheduled(
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]

    now = datetime.now(timezone.utc)

    trip.departure_time = (
        now + timedelta(hours=3)
    )

    trip.arrival_time = (
        now + timedelta(hours=13)
    )

    db.commit()

    count = update_boarding_trips(
        db,
        now,
    )

    db.commit()
    db.refresh(trip)

    assert count == 0
    assert trip.status == TripStatus.SCHEDULED


def test_missing_scheduled_trip_is_recovered(
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]
    train = seeded_data["train"]

    trip.status = TripStatus.DEPARTED

    db.commit()

    count = (
        ensure_scheduled_trip_for_active_trains(
            db
        )
    )

    db.commit()

    assert count == 1

    scheduled = db.scalar(
        select(Trip)
        .where(
            Trip.train_id == train.id,
            Trip.status == TripStatus.SCHEDULED,
        )
    )

    assert scheduled is not None

    assert (
        scheduled.direction
        == TripDirection.REVERSE
    )


def test_existing_scheduled_trip_not_duplicated(
    db: Session,
    seeded_data: dict,
):
    train = seeded_data["train"]

    count = (
        ensure_scheduled_trip_for_active_trains(
            db
        )
    )

    db.commit()

    trips = list(
        db.scalars(
            select(Trip)
            .where(
                Trip.train_id == train.id,
                Trip.status
                == TripStatus.SCHEDULED,
            )
        ).all()
    )

    assert count == 0
    assert len(trips) == 1