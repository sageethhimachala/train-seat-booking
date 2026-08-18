from fastapi.testclient import TestClient


def test_get_stations_returns_stations_in_order(
    client: TestClient,
    seeded_data: dict,
):
    response = client.get("/api/v1/stations")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 4

    assert data[0]["name"] == "Colombo Fort"
    assert data[0]["code"] == "FOT"

    assert data[1]["name"] == "Ragama"

    assert data[2]["name"] == "Kandy"

    assert data[3]["name"] == "Badulla"


def test_station_order_index_is_sorted(
    client: TestClient,
    seeded_data: dict,
):
    response = client.get("/api/v1/stations")

    data = response.json()

    indexes = [
        station["order_index"]
        for station in data
    ]

    assert indexes == sorted(indexes)