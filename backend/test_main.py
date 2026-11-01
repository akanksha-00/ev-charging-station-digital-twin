from urllib import response

from fastapi.testclient import TestClient
from requests import session
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
        json={"id": "CP-NO-DUP-01", "max_power_kw": 12.0},
    )

    assert response.status_code == 201

    lookup = client.post(
        "/sessions",
        json={
            "charger_id": "CP-NO-DUP-01",
            "target_energy_kwh": 20.0,
        },
    )

    assert lookup.status_code == 201

    session_data = lookup.json()
    assert session_data["charger_id"] == "CP-NO-DUP-01"
    assert session_data["status"] == "active"

    charger_response = client.get(
        "/chargers/CP-NO-DUP-01",
    )
    charger_data = charger_response.json()
    assert charger_response.status_code == 200
    assert charger_data["status"] == "charging"

    duplicate_session_response = client.post(
        "/sessions",
        json={
            "charger_id": "CP-NO-DUP-01",
            "target_energy_kwh": 20.0,
        },
    )

    assert duplicate_session_response.status_code == 409


def test_missing_session_id(client):
    response = client.get("/sessions/00000000-0000-0000-0000-000000000001")

    assert response.status_code == 404


def test_invalid_session_id(client):
    response = client.get("/sessions/invalid-session-id")

    assert response.status_code == 422


def test_stop_charging_session(client):

    # create charger
    response = client.post(
        "/chargers",
        json={"id": "CP-STOP-01", "max_power_kw": 12.0},
    )

    assert response.status_code == 201

    # create session
    lookup = client.post(
        "/sessions",
        json={
            "charger_id": "CP-STOP-01",
            "target_energy_kwh": 20.0,
        },
    )

    assert lookup.status_code == 201

    session_data = lookup.json()
    session_id = session_data["id"]

    # stop session
    stop_charging_session_response = client.post(
        f"/sessions/{session_id}/stop",
    )

    assert stop_charging_session_response.status_code == 200

    stopped_session = stop_charging_session_response.json()

    assert stopped_session["id"] == session_id
    assert stopped_session["status"] == "stopped"
    assert stopped_session["end_time"] is not None

    # verify session is stopped
    charging_session_lookup_respone = client.get(f"/sessions/{session_id}")

    assert charging_session_lookup_respone.status_code == 200

    charging_session_lookup = charging_session_lookup_respone.json()
    charger_id = charging_session_lookup["charger_id"]
    assert charging_session_lookup == stopped_session

    # verify charger status changed
    charger_lookup_response = client.get(f"/chargers/{charger_id}")

    assert charger_lookup_response.status_code == 200

    charger_lookup = charger_lookup_response.json()
    assert charger_lookup["status"] == "available"

    # test for concurrency
    new_charging_session_response = client.post(
        "/sessions",
        json={
            "charger_id": "CP-STOP-01",
            "target_energy_kwh": 22.0,
        },
    )

    assert new_charging_session_response.status_code == 201
    new_charging_session = new_charging_session_response.json()
    new_charging_session_id = new_charging_session["id"]
    assert new_charging_session["status"] == "active"

    # stop the previous session
    repeated_stop_session_response = client.post(
        f"/sessions/{session_id}/stop",
    )

    assert repeated_stop_session_response.status_code == 200
    assert repeated_stop_session_response.json() == stopped_session

    # verify that second session is not affected
    new_charging_session_response = client.get(
        f"/sessions/{new_charging_session_id}",
    )
    
    assert new_charging_session_response.status_code == 200
    assert new_charging_session_response.json() == new_charging_session
    
    # verify the charger status
    charger_lookup = client.get(f"/chargers/{charger_id}")
    
    assert charger_lookup.status_code == 200
    charger_lookup = charger_lookup.json()
    
    assert charger_lookup["status"] == "charging"
