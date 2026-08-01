from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
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


STATIONS = [
    {
        "name": "Colombo Fort",
        "code": "FOT",
        "order_index": 0,
        "distance": "0.00",
    },
    {
        "name": "Ragama",
        "code": "RGM",
        "order_index": 1,
        "distance": "13.70",
    },
    {
        "name": "Gampaha",
        "code": "GPH",
        "order_index": 2,
        "distance": "27.60",
    },
    {
        "name": "Polgahawela",
        "code": "PLG",
        "order_index": 3,
        "distance": "73.90",
    },
    {
        "name": "Rambukkana",
        "code": "RBK",
        "order_index": 4,
        "distance": "84.80",
    },
    {
        "name": "Kandy",
        "code": "KDT",
        "order_index": 5,
        "distance": "120.70",
    },
    {
        "name": "Nanu Oya",
        "code": "NOA",
        "order_index": 6,
        "distance": "206.90",
    },
    {
        "name": "Haputale",
        "code": "HPT",
        "order_index": 7,
        "distance": "247.00",
    },
    {
        "name": "Ella",
        "code": "ELL",
        "order_index": 8,
        "distance": "271.00",
    },
    {
        "name": "Badulla",
        "code": "BAD",
        "order_index": 9,
        "distance": "292.30",
    },
]


def get_future_time(hours_from_now: int) -> datetime:
    now = datetime.now(timezone.utc)

    return (
        now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        + timedelta(hours=hours_from_now)
    )


def clear_database(db: Session) -> None:
    db.execute(delete(Booking))
    db.execute(delete(Trip))
    db.execute(delete(Seat))
    db.execute(delete(Coach))
    db.execute(delete(Train))
    db.execute(delete(Station))


def create_stations(db: Session) -> list[Station]:
    stations = []

    for station_data in STATIONS:
        station = Station(
            name=station_data["name"],
            code=station_data["code"],
            order_index=station_data["order_index"],
            distance_from_start_km=Decimal(
                station_data["distance"]
            ),
        )

        stations.append(station)

    db.add_all(stations)
    db.flush()

    return stations


def create_train_with_coaches_and_seats(
    db: Session,
) -> Train:
    train = Train(
        train_number="1005",
        name="Podi Menike",
        is_active=True,
    )

    # Reserved coaches: 1, 2 and 3.
    for coach_number in range(1, 4):
        coach = Coach(
            coach_number=coach_number,
            coach_type=CoachType.RESERVED,
        )

        # Ten seats per reserved coach.
        for seat_number in range(1, 11):
            seat = Seat(
                seat_number=f"{seat_number:02d}",
            )

            coach.seats.append(seat)

        train.coaches.append(coach)

    # Unreserved coaches: 4 to 8.
    for coach_number in range(4, 9):
        coach = Coach(
            coach_number=coach_number,
            coach_type=CoachType.UNRESERVED,
        )

        train.coaches.append(coach)

    db.add(train)
    db.flush()

    return train


def create_trips(
    db: Session,
    train: Train,
    stations: list[Station],
) -> None:
    colombo = stations[0]
    badulla = stations[-1]

    first_forward_departure = get_future_time(2)
    reverse_departure = get_future_time(14)
    second_forward_departure = get_future_time(26)

    trips = [
        Trip(
            train_id=train.id,
            start_station_id=colombo.id,
            end_station_id=badulla.id,
            departure_time=first_forward_departure,
            arrival_time=(
                first_forward_departure
                + timedelta(hours=10)
            ),
            direction=TripDirection.FORWARD,
            status=TripStatus.SCHEDULED,
        ),
        Trip(
            train_id=train.id,
            start_station_id=badulla.id,
            end_station_id=colombo.id,
            departure_time=reverse_departure,
            arrival_time=(
                reverse_departure
                + timedelta(hours=10)
            ),
            direction=TripDirection.REVERSE,
            status=TripStatus.SCHEDULED,
        ),
        Trip(
            train_id=train.id,
            start_station_id=colombo.id,
            end_station_id=badulla.id,
            departure_time=second_forward_departure,
            arrival_time=(
                second_forward_departure
                + timedelta(hours=10)
            ),
            direction=TripDirection.FORWARD,
            status=TripStatus.SCHEDULED,
        ),
    ]

    db.add_all(trips)


def seed_database() -> None:
    with SessionLocal() as db:
        try:
            existing_train = db.scalar(
                select(Train).where(
                    Train.train_number == "1005"
                )
            )

            if existing_train is not None:
                print(
                    "Seed data already exists. "
                    "Run with --reset to recreate it."
                )
                return

            stations = create_stations(db)

            train = create_train_with_coaches_and_seats(
                db
            )

            create_trips(
                db,
                train,
                stations,
            )

            db.commit()

            print("Seed data created successfully.")
            print(f"Stations: {len(stations)}")
            print("Reserved coaches: 3")
            print("Unreserved coaches: 5")
            print("Reserved seats: 30")
            print("Trips: 3")

        except Exception:
            db.rollback()
            raise


def reset_and_seed_database() -> None:
    with SessionLocal() as db:
        try:
            clear_database(db)

            stations = create_stations(db)

            train = create_train_with_coaches_and_seats(
                db
            )

            create_trips(
                db,
                train,
                stations,
            )

            db.commit()

            print(
                "Database reset and seeded successfully."
            )

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed the train booking database."
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing data before seeding.",
    )

    args = parser.parse_args()

    if args.reset:
        reset_and_seed_database()
    else:
        seed_database()
