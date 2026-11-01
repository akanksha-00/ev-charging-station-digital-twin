from urllib import response

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


def test_rejects_zero_max_power(client):
    response = client.post(
        "/chargers",
        json={"id": "CP-INVALID", "max_power_kw": 0},
    )

    assert response.status_code == 422

    lookup = client.get("/chargers/CP-INVALID")

    assert lookup.status_code == 404


def test_create_and_get_charger(client):
    response = client.post(
        "/chargers",
        json={"id": "CP-TEST-01", "max_power_kw": 12.0},
    )

    assert response.status_code == 201

    expected = {
        "id": "CP-TEST-01",
        "status": "available",
        "max_power_kw": 12.0,
        "current_power_kw": 0.0,
        "energy_delivered_kwh": 0.0,
    }

    assert response.json() == expected

    lookup = client.get("/chargers/CP-TEST-01")

    assert lookup.status_code == 200
    assert lookup.json() == expected


def test_rejects_existing_charger_id(client):
    response = client.post(
        "/chargers",
        json={"id": "CP-TEST-01", "max_power_kw": 12.0},
    )

    assert response.status_code == 201

    lookup = client.post(
        "/chargers",
        json={"id": "CP-TEST-01", "max_power_kw": 12.0},
    )

    assert lookup.status_code == 409


def test_start_charging_session(client):
    response = client.post(
        "/chargers",
        json={"id": "CP-TEST-01", "max_power_kw": 12.0},
    )

    assert response.status_code == 201

    lookup = client.post(
        "/sessions",
        json={
            "charger_id": "CP-TEST-01",
            "target_energy_kwh": 20.0,
        },
    )

    assert lookup.status_code == 201

    session_data = lookup.json()

    assert session_data["charger_id"] == "CP-TEST-01"
    assert session_data["status"] == "active"
    assert session_data["target_energy_kwh"] == 20.0
    assert session_data["energy_delivered_kwh"] == 0.0
    assert session_data["end_time"] == None

    charger_response = client.get(
        "/chargers/CP-TEST-01",
    )

    charger_data = charger_response.json()

    assert charger_response.status_code == 200
    assert charger_data["status"] == "charging"


def test_no_duplicate_charging_session_with_same_charging_id(client):
    response = client.post(
        "/chargers",
        json={"id": "CP-TEST-01", "max_power_kw": 12.0},
    )

    assert response.status_code == 201

    lookup = client.post(
        "/sessions",
        json={
            "charger_id": "CP-TEST-01",
            "target_energy_kwh": 20.0,
        },
    )

    assert lookup.status_code == 201

    session_data = lookup.json()
    assert session_data["charger_id"] == "CP-TEST-01"
    assert session_data["status"] == "active"

    charger_response = client.get(
        "/chargers/CP-TEST-01",
    )
    charger_data = charger_response.json()
    assert charger_response.status_code == 200
    assert charger_data["status"] == "charging"

    duplicate_session_response = client.post(
        "/sessions",
        json={
            "charger_id": "CP-TEST-01",
            "target_energy_kwh": 20.0,
        },
    )

    assert duplicate_session_response.status_code == 409
