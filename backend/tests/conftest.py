import os
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.database.database import Base, get_db
from app.main import app
from app.models.models import (
    Booking,
    Coach,
    CoachType,
    Seat,
    Station,
    Train,
    Trip,
    TripDirection,
    TripStatus,
)


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL environment variable is required."
    )


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_schema():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_database():
    with TestingSessionLocal() as db:
        db.execute(delete(Booking))
        db.execute(delete(Trip))
        db.execute(delete(Seat))
        db.execute(delete(Coach))
        db.execute(delete(Train))
        db.execute(delete(Station))
        db.commit()

    yield


@pytest.fixture
def db() -> Generator[Session, None, None]:
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:

    # Prevent APScheduler from running during API tests.
    monkeypatch.setattr(
        "app.main.start_trip_scheduler",
        lambda: None,
    )

    monkeypatch.setattr(
        "app.main.stop_trip_scheduler",
        lambda: None,
    )

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_data(
    db: Session,
) -> dict:
    now = datetime.now(timezone.utc)

    stations = [
        Station(
            name="Colombo Fort",
            code="FOT",
            order_index=0,
            distance_from_start_km=Decimal("0.00"),
        ),
        Station(
            name="Ragama",
            code="RGM",
            order_index=1,
            distance_from_start_km=Decimal("13.70"),
        ),
        Station(
            name="Kandy",
            code="KDT",
            order_index=2,
            distance_from_start_km=Decimal("120.70"),
        ),
        Station(
            name="Badulla",
            code="BAD",
            order_index=3,
            distance_from_start_km=Decimal("292.30"),
        ),
    ]

    db.add_all(stations)
    db.flush()

    train = Train(
        train_number="1005",
        name="Podi Menike",
        is_active=True,
        boarding_minutes_before=30,
        turnaround_minutes=60,
    )

    reserved_coach = Coach(
        coach_number=1,
        coach_type=CoachType.RESERVED,
    )

    reserved_coach.seats.extend(
        [
            Seat(seat_number="01"),
            Seat(seat_number="02"),
        ]
    )

    unreserved_coach = Coach(
        coach_number=2,
        coach_type=CoachType.UNRESERVED,
    )

    train.coaches.extend(
        [
            reserved_coach,
            unreserved_coach,
        ]
    )

    db.add(train)
    db.flush()

    trip = Trip(
        train_id=train.id,
        start_station_id=stations[0].id,
        end_station_id=stations[3].id,
        departure_time=now + timedelta(hours=2),
        arrival_time=now + timedelta(hours=12),
        direction=TripDirection.FORWARD,
        status=TripStatus.SCHEDULED,
    )

    db.add(trip)
    db.commit()

    seat_1 = db.query(Seat).filter(
        Seat.coach_id == reserved_coach.id,
        Seat.seat_number == "01",
    ).one()

    seat_2 = db.query(Seat).filter(
        Seat.coach_id == reserved_coach.id,
        Seat.seat_number == "02",
    ).one()

    return {
        "stations": stations,
        "train": train,
        "trip": trip,
        "reserved_coach": reserved_coach,
        "seat_1": seat_1,
        "seat_2": seat_2,
    }