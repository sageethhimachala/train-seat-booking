from fastapi.testclient import TestClient


def test_forward_availability(
    client: TestClient,
    seeded_data: dict,
):
    stations = seeded_data["stations"]

    response = client.get(
        "/api/v1/availability",
        params={
            "origin_station_id": stations[0].id,
            "destination_station_id": stations[2].id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["trip"] is not None

    assert data["trip"]["direction"] == "FORWARD"

    assert len(data["available_seats"]) == 2


def test_only_reserved_seats_are_returned(
    client: TestClient,
    seeded_data: dict,
):
    stations = seeded_data["stations"]

    response = client.get(
        "/api/v1/availability",
        params={
            "origin_station_id": stations[0].id,
            "destination_station_id": stations[2].id,
        },
    )

    data = response.json()

    coach_numbers = {
        seat["coach_number"]
        for seat in data["available_seats"]
    }

    assert coach_numbers == {1}


def test_same_origin_and_destination_rejected(
    client: TestClient,
    seeded_data: dict,
):
    station_id = seeded_data["stations"][0].id

    response = client.get(
        "/api/v1/availability",
        params={
            "origin_station_id": station_id,
            "destination_station_id": station_id,
        },
    )

    assert response.status_code == 400


def test_unknown_station_returns_404(
    client: TestClient,
    seeded_data: dict,
):
    destination = seeded_data["stations"][2]

    response = client.get(
        "/api/v1/availability",
        params={
            "origin_station_id": 999999,
            "destination_station_id": destination.id,
        },
    )

    assert response.status_code == 404


def test_reverse_search_returns_no_trip(
    client: TestClient,
    seeded_data: dict,
):
    stations = seeded_data["stations"]

    response = client.get(
        "/api/v1/availability",
        params={
            "origin_station_id": stations[3].id,
            "destination_station_id": stations[1].id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["trip"] is None
    assert data["available_seats"] == []