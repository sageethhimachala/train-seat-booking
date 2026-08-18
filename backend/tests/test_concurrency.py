from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient


def test_concurrent_booking_only_one_succeeds(
    client: TestClient,
    seeded_data: dict,
):
    stations = seeded_data["stations"]
    trip = seeded_data["trip"]
    seat = seeded_data["seat_1"]

    def send_request(number: int):
        return client.post(
            "/api/v1/bookings",
            json={
                "trip_id": trip.id,
                "seat_id": seat.id,
                "origin_station_id": stations[0].id,
                "destination_station_id": stations[2].id,
                "passenger_name": (
                    f"Passenger {number}"
                ),
                "passenger_email": (
                    f"passenger{number}@example.com"
                ),
            },
        )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        responses = list(
            executor.map(
                send_request,
                [1, 2],
            )
        )

    status_codes = sorted(
        response.status_code
        for response in responses
    )

    assert status_codes == [201, 409]