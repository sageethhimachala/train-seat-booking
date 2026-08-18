from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.models import (
    Booking,
    BookingStatus,
    TripStatus,
)


def make_booking_payload(
    seeded_data: dict,
    *,
    origin_index: int = 0,
    destination_index: int = 2,
    seat_key: str = "seat_1",
):
    stations = seeded_data["stations"]
    trip = seeded_data["trip"]
    seat = seeded_data[seat_key]

    return {
        "trip_id": trip.id,
        "seat_id": seat.id,
        "origin_station_id": stations[
            origin_index
        ].id,
        "destination_station_id": stations[
            destination_index
        ].id,
        "passenger_name": "Test Passenger",
        "passenger_email": "test@example.com",
    }


def test_create_booking(
    client: TestClient,
    seeded_data: dict,
):
    response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "CONFIRMED"

    assert data["booking_reference"].startswith(
        "TRN-"
    )

    assert (
        data["passenger_name"]
        == "Test Passenger"
    )

    assert data["seat"]["seat_number"] == "01"

    assert (
        data["origin_station"]["name"]
        == "Colombo Fort"
    )

    assert (
        data["destination_station"]["name"]
        == "Kandy"
    )


def test_overlapping_segment_is_rejected(
    client: TestClient,
    seeded_data: dict,
):
    first = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(
            seeded_data,
            origin_index=0,
            destination_index=2,
        ),
    )

    assert first.status_code == 201

    # Existing:
    # Colombo -> Kandy
    #
    # Attempt:
    # Ragama -> Badulla
    #
    # These segments overlap.
    second = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(
            seeded_data,
            origin_index=1,
            destination_index=3,
        ),
    )

    assert second.status_code == 409

def test_adjacent_segment_is_allowed(
    client: TestClient,
    seeded_data: dict,
):
    first = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(
            seeded_data,
            origin_index=0,
            destination_index=2,
        ),
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(
            seeded_data,
            origin_index=2,
            destination_index=3,
        ),
    )

    assert second.status_code == 201


def test_different_seat_same_segment_allowed(
    client: TestClient,
    seeded_data: dict,
):
    first = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(
            seeded_data,
            seat_key="seat_1",
        ),
    )

    second = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(
            seeded_data,
            seat_key="seat_2",
        ),
    )

    assert first.status_code == 201
    assert second.status_code == 201


def test_booking_lookup(
    client: TestClient,
    seeded_data: dict,
):
    create_response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    reference = create_response.json()[
        "booking_reference"
    ]

    response = client.get(
        f"/api/v1/bookings/{reference}"
    )

    assert response.status_code == 200

    assert (
        response.json()["booking_reference"]
        == reference
    )


def test_booking_lookup_case_insensitive(
    client: TestClient,
    seeded_data: dict,
):
    create_response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    reference = create_response.json()[
        "booking_reference"
    ]

    response = client.get(
        f"/api/v1/bookings/{reference.lower()}"
    )

    assert response.status_code == 200


def test_cancel_booking(
    client: TestClient,
    seeded_data: dict,
):
    create_response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    reference = create_response.json()[
        "booking_reference"
    ]

    response = client.post(
        f"/api/v1/bookings/{reference}/cancel"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "CANCELLED"
    assert data["cancelled_at"] is not None


def test_cancelled_booking_releases_seat(
    client: TestClient,
    seeded_data: dict,
):
    payload = make_booking_payload(seeded_data)

    create_response = client.post(
        "/api/v1/bookings",
        json=payload,
    )

    reference = create_response.json()[
        "booking_reference"
    ]

    cancel_response = client.post(
        f"/api/v1/bookings/{reference}/cancel"
    )

    assert cancel_response.status_code == 200

    new_payload = {
        **payload,
        "passenger_name": "Second Passenger",
        "passenger_email": "second@example.com",
    }

    response = client.post(
        "/api/v1/bookings",
        json=new_payload,
    )

    assert response.status_code == 201


def test_cannot_cancel_twice(
    client: TestClient,
    seeded_data: dict,
):
    create_response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    reference = create_response.json()[
        "booking_reference"
    ]

    first = client.post(
        f"/api/v1/bookings/{reference}/cancel"
    )

    second = client.post(
        f"/api/v1/bookings/{reference}/cancel"
    )

    assert first.status_code == 200
    assert second.status_code == 409


def test_cannot_book_departed_trip(
    client: TestClient,
    db: Session,
    seeded_data: dict,
):
    trip = seeded_data["trip"]

    trip.status = TripStatus.DEPARTED
    trip.departure_time = datetime.now(
        timezone.utc
    )

    db.commit()

    response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    assert response.status_code == 409


def test_cannot_cancel_after_departure(
    client: TestClient,
    db: Session,
    seeded_data: dict,
):
    create_response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    assert create_response.status_code == 201

    reference = create_response.json()[
        "booking_reference"
    ]

    trip = seeded_data["trip"]
    trip.status = TripStatus.DEPARTED

    db.commit()

    response = client.post(
        f"/api/v1/bookings/{reference}/cancel"
    )

    assert response.status_code == 409


def test_cancelled_status_persisted(
    client: TestClient,
    db: Session,
    seeded_data: dict,
):
    create_response = client.post(
        "/api/v1/bookings",
        json=make_booking_payload(seeded_data),
    )

    reference = create_response.json()[
        "booking_reference"
    ]

    client.post(
        f"/api/v1/bookings/{reference}/cancel"
    )

    booking = db.query(Booking).filter(
        Booking.booking_reference == reference
    ).one()

    db.refresh(booking)

    assert booking.status == BookingStatus.CANCELLED
    assert booking.cancelled_at is not None