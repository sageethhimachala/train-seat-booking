from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Enum
)

from sqlalchemy.orm import relationship

from app.database.database import Base

import enum

class CoachType(enum.Enum):

    RESERVED = "RESERVED"

    UNRESERVED = "UNRESERVED"



class TripStatus(enum.Enum):

    SCHEDULED = "SCHEDULED"

    BOARDING = "BOARDING"

    DEPARTED = "DEPARTED"

    COMPLETED = "COMPLETED"



class Direction(enum.Enum):

    FORWARD = "FORWARD"

    REVERSE = "REVERSE"


class Station(Base):

    __tablename__ = "stations"


    id = Column(
        Integer,
        primary_key=True
    )


    name = Column(
        String,
        nullable=False
    )


    order_index = Column(
        Integer,
        nullable=False
    )


    distance_km = Column(
        Float
    )


class Train(Base):

    __tablename__ = "trains"


    id = Column(
        Integer,
        primary_key=True
    )


    name = Column(
        String,
        nullable=False
    )


class Coach(Base):

    __tablename__ = "coaches"


    id = Column(
        Integer,
        primary_key=True
    )


    train_id = Column(
        ForeignKey("trains.id")
    )


    coach_number = Column(
        Integer
    )


    type = Column(
        Enum(CoachType)
    )

class Seat(Base):

    __tablename__ = "seats"


    id = Column(
        Integer,
        primary_key=True
    )


    coach_id = Column(
        ForeignKey("coaches.id")
    )


    seat_number = Column(
        String
    )

class Trip(Base):

    __tablename__ = "trips"


    id = Column(
        Integer,
        primary_key=True
    )


    train_id = Column(
        ForeignKey("trains.id")
    )


    start_station_id = Column(
        ForeignKey("stations.id")
    )


    end_station_id = Column(
        ForeignKey("stations.id")
    )


    departure_time = Column(
        DateTime
    )


    arrival_time = Column(
        DateTime
    )


    direction = Column(
        Enum(Direction)
    )


    status = Column(
        Enum(TripStatus)
    )

class Booking(Base):

    __tablename__ = "bookings"


    id = Column(
        Integer,
        primary_key=True
    )


    trip_id = Column(
        ForeignKey("trips.id")
    )


    seat_id = Column(
        ForeignKey("seats.id")
    )


    origin_station_id = Column(
        ForeignKey("stations.id")
    )


    destination_station_id = Column(
        ForeignKey("stations.id")
    )


    passenger_name = Column(
        String
    )


    fare = Column(
        Float
    )

