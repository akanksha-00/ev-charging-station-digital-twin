from fastapi.testclient import TestClient
from schemas import Charger
from main import app

chargers_test = chargers = [
    Charger(
        id="CP-01",
        status="available",
        max_power_kw="11.0",
        current_power_kw=0.0,
        energy_delivered_kwh="0.0",
    )
]


def test_rejects_zero_max_power():
    with TestClient(app) as client:
        response = client.post(
            "/chargers",
            json={"id": "CP-INVALID", "max_power_kw": 0},
        )

        assert response.status_code == 422

        lookup = client.get("/chargers/CP-INVALID")

        assert lookup.status_code == 404
        
def test_rejects_existing_charger_id():
    with TestClient(app) as client:
        response = client.post(
            "/chargers",
            json={"id": "CP-01", "max_power_kw": 12},
        )

        assert response.status_code == 409