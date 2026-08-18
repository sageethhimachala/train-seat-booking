from fastapi.testclient import TestClient


def test_root_endpoint(
    client: TestClient,
):
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Train Seat Booking API is running"
    }


def test_health_endpoint(
    client: TestClient,
):
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }