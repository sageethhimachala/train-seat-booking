from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class CoachType(str, enum.Enum):
    RESERVED = "RESERVED"
    UNRESERVED = "UNRESERVED"


class TripDirection(str, enum.Enum):
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"


class TripStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    BOARDING = "BOARDING"
    DEPARTED = "DEPARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class BookingStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    distance_from_start_km: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "order_index >= 0",
            name="ck_station_order_non_negative",
        ),
        CheckConstraint(
            "distance_from_start_km >= 0",
            name="ck_station_distance_non_negative",
        ),
    )


class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    coaches: Mapped[list[Coach]] = relationship(
        back_populates="train",
        cascade="all, delete-orphan",
    )

    trips: Mapped[list[Trip]] = relationship(
        back_populates="train",
        cascade="all, delete-orphan",
    )


class Coach(Base):
    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(primary_key=True)

    train_id: Mapped[int] = mapped_column(
        ForeignKey("trains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    coach_number: Mapped[int] = mapped_column(Integer, nullable=False)

    coach_type: Mapped[CoachType] = mapped_column(
        Enum(
            CoachType,
            name="coach_type",
            native_enum=True,
        ),
        nullable=False,
    )

    train: Mapped[Train] = relationship(back_populates="coaches")

    seats: Mapped[list[Seat]] = relationship(
        back_populates="coach",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "coach_number",
            name="uq_coach_train_number",
        ),
        CheckConstraint(
            "coach_number > 0",
            name="ck_coach_number_positive",
        ),
    )


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(primary_key=True)

    coach_id: Mapped[int] = mapped_column(
        ForeignKey("coaches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)

    coach: Mapped[Coach] = relationship(back_populates="seats")

    bookings: Mapped[list[Booking]] = relationship(back_populates="seat")

    __table_args__ = (
        UniqueConstraint(
            "coach_id",
            "seat_number",
            name="uq_seat_coach_number",
        ),
    )


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True)

    train_id: Mapped[int] = mapped_column(
        ForeignKey("trains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id"),
        nullable=False,
    )

    end_station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id"),
        nullable=False,
    )

    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    direction: Mapped[TripDirection] = mapped_column(
        Enum(
            TripDirection,
            name="trip_direction",
            native_enum=True,
        ),
        nullable=False,
    )

    status: Mapped[TripStatus] = mapped_column(
        Enum(
            TripStatus,
            name="trip_status",
            native_enum=True,
        ),
        nullable=False,
        default=TripStatus.SCHEDULED,
        index=True,
    )

    train: Mapped[Train] = relationship(back_populates="trips")

    start_station: Mapped[Station] = relationship(
        foreign_keys=[start_station_id]
    )

    end_station: Mapped[Station] = relationship(
        foreign_keys=[end_station_id]
    )

    bookings: Mapped[list[Booking]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "start_station_id <> end_station_id",
            name="ck_trip_different_terminal_stations",
        ),
        CheckConstraint(
            "arrival_time > departure_time",
            name="ck_trip_arrival_after_departure",
        ),
        UniqueConstraint(
            "train_id",
            "departure_time",
            name="uq_train_departure_time",
        ),
        Index(
            "ix_trip_search",
            "status",
            "direction",
            "departure_time",
        ),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_reference: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )

    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.id"),
        nullable=False,
        index=True,
    )

    origin_station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id"),
        nullable=False,
    )

    destination_station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id"),
        nullable=False,
    )

    passenger_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    passenger_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    fare: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[BookingStatus] = mapped_column(
        Enum(
            BookingStatus,
            name="booking_status",
            native_enum=True,
        ),
        nullable=False,
        default=BookingStatus.CONFIRMED,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    trip: Mapped[Trip] = relationship(back_populates="bookings")

    seat: Mapped[Seat] = relationship(back_populates="bookings")

    origin_station: Mapped[Station] = relationship(
        foreign_keys=[origin_station_id]
    )

    destination_station: Mapped[Station] = relationship(
        foreign_keys=[destination_station_id]
    )

    __table_args__ = (
        CheckConstraint(
            "origin_station_id <> destination_station_id",
            name="ck_booking_different_stations",
        ),
        CheckConstraint(
            "fare >= 0",
            name="ck_booking_fare_non_negative",
        ),
        CheckConstraint(
            """
            (status = 'CONFIRMED' AND cancelled_at IS NULL)
            OR
            (status = 'CANCELLED' AND cancelled_at IS NOT NULL)
            """,
            name="ck_booking_cancelled_timestamp",
        ),
        Index(
            "ix_booking_overlap_search",
            "trip_id",
            "seat_id",
            "status",
        ),
    )