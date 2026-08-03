import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database.database import SessionLocal
from app.models.models import (
    Train,
    Trip,
    TripDirection,
    TripStatus,
)


logger = logging.getLogger(__name__)


SCHEDULER_LOCK_ID = 730001


def reverse_direction(
    direction: TripDirection,
) -> TripDirection:
    if direction == TripDirection.FORWARD:
        return TripDirection.REVERSE

    return TripDirection.FORWARD


def create_next_trip(
    db: Session,
    current_trip: Trip,
) -> Trip:
    train = current_trip.train

    next_departure = (
        current_trip.arrival_time
        + timedelta(
            minutes=train.turnaround_minutes
        )
    )

    current_duration = (
        current_trip.arrival_time
        - current_trip.departure_time
    )

    next_arrival = next_departure + current_duration

    next_trip = Trip(
        train_id=current_trip.train_id,

        # The previous destination becomes the
        # starting terminal of the reverse trip.
        start_station_id=current_trip.end_station_id,
        end_station_id=current_trip.start_station_id,

        departure_time=next_departure,
        arrival_time=next_arrival,

        direction=reverse_direction(
            current_trip.direction
        ),

        status=TripStatus.SCHEDULED,
    )

    db.add(next_trip)
    db.flush()

    logger.info(
        "Created next trip %s for train %s: %s -> %s",
        next_trip.id,
        train.train_number,
        next_trip.start_station_id,
        next_trip.end_station_id,
    )

    return next_trip


def update_completed_trips(
    db: Session,
    now: datetime,
) -> int:
    statement = (
        select(Trip)
        .where(
            Trip.status == TripStatus.DEPARTED,
            Trip.arrival_time <= now,
        )
        .with_for_update(skip_locked=True)
    )

    trips = list(db.scalars(statement).all())

    for trip in trips:
        trip.status = TripStatus.COMPLETED

        logger.info(
            "Trip %s changed from DEPARTED to COMPLETED",
            trip.id,
        )

    return len(trips)


def update_departed_trips(
    db: Session,
    now: datetime,
) -> int:
    statement = (
        select(Trip)
        .where(
            Trip.status == TripStatus.BOARDING,
            Trip.departure_time <= now,
        )
        .with_for_update(skip_locked=True)
    )

    trips = list(db.scalars(statement).all())

    for trip in trips:
        trip.status = TripStatus.DEPARTED

        logger.info(
            "Trip %s changed from BOARDING to DEPARTED",
            trip.id,
        )

    return len(trips)


def update_boarding_trips(
    db: Session,
    now: datetime,
) -> int:
    statement = (
        select(Trip)
        .options(
            joinedload(Trip.train),
        )
        .join(Trip.train)
        .where(
            Trip.status == TripStatus.SCHEDULED,
            Train.is_active.is_(True),
        )
        .with_for_update(
            of=Trip,
            skip_locked=True,
        )
    )

    scheduled_trips = list(
        db.scalars(statement).all()
    )

    changed_count = 0

    for trip in scheduled_trips:
        boarding_time = (
            trip.departure_time
            - timedelta(
                minutes=(
                    trip.train.boarding_minutes_before
                )
            )
        )

        if boarding_time > now:
            continue

        trip.status = TripStatus.BOARDING

        # Flush the status change before creating the
        # next SCHEDULED trip. Otherwise, the partial
        # unique index would still see this trip as
        # SCHEDULED.
        db.flush()

        create_next_trip(
            db=db,
            current_trip=trip,
        )

        changed_count += 1

        logger.info(
            "Trip %s changed from SCHEDULED to BOARDING",
            trip.id,
        )

    return changed_count


def ensure_scheduled_trip_for_active_trains(
    db: Session,
) -> int:
    active_trains = list(
        db.scalars(
            select(Train)
            .where(Train.is_active.is_(True))
            .options(
                joinedload(Train.trips),
            )
        )
        .unique()
        .all()
    )

    created_count = 0

    for train in active_trains:
        scheduled_trip = db.scalar(
            select(Trip.id)
            .where(
                Trip.train_id == train.id,
                Trip.status == TripStatus.SCHEDULED,
            )
            .limit(1)
        )

        if scheduled_trip is not None:
            continue

        latest_trip = db.scalar(
            select(Trip)
            .options(
                joinedload(Trip.train),
            )
            .where(
                Trip.train_id == train.id,
                Trip.status.in_(
                    [
                        TripStatus.BOARDING,
                        TripStatus.DEPARTED,
                        TripStatus.COMPLETED,
                    ]
                ),
            )
            .order_by(
                Trip.departure_time.desc()
            )
            .limit(1)
        )

        if latest_trip is None:
            logger.warning(
                "Train %s has no trips. "
                "An initial trip must be created manually.",
                train.train_number,
            )
            continue

        create_next_trip(
            db=db,
            current_trip=latest_trip,
        )

        created_count += 1

    return created_count


def run_trip_scheduler_cycle() -> None:
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        try:
            # PostgreSQL transaction-level advisory lock.
            #
            # If multiple API processes run this scheduler,
            # only one process performs the update cycle.
            lock_acquired = db.execute(
                text(
                    "SELECT pg_try_advisory_xact_lock"
                    "(:lock_id)"
                ),
                {
                    "lock_id": SCHEDULER_LOCK_ID,
                },
            ).scalar_one()

            if not lock_acquired:
                logger.info(
                    "Trip scheduler cycle skipped because "
                    "another process owns the lock."
                )
                db.rollback()
                return

            completed_count = update_completed_trips(
                db,
                now,
            )

            departed_count = update_departed_trips(
                db,
                now,
            )

            boarding_count = update_boarding_trips(
                db,
                now,
            )

            recovered_count = (
                ensure_scheduled_trip_for_active_trains(
                    db
                )
            )

            db.commit()

            logger.info(
                (
                    "Trip scheduler cycle completed: "
                    "completed=%s, departed=%s, "
                    "boarding=%s, recovered=%s"
                ),
                completed_count,
                departed_count,
                boarding_count,
                recovered_count,
            )

        except IntegrityError:
            db.rollback()

            logger.exception(
                "Trip scheduler encountered a "
                "database integrity error."
            )

        except Exception:
            db.rollback()

            logger.exception(
                "Trip scheduler cycle failed."
            )