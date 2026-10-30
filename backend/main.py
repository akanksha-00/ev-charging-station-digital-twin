from turtle import title
from schemas import Charger, AddCharger
from fastapi import FastAPI, HTTPException

app = FastAPI(title="EV Charging Digital Twin API")

chargers = [
    Charger(
        id="CP-01",
        status="available",
        max_power_kw="11.0",
        current_power_kw=0.0,
        energy_delivered_kwh="0.0",
    )
]

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.get("/chargers", response_model=list[Charger])
def get_chargers():
    return chargers

@app.get("/chargers/{charger_id}", response_model=Charger)
def get_charger_by_id(charger_id: str):
    for charger in chargers:
        if charger.id == charger_id:
            return charger
    raise HTTPException(status_code=404, detail="Charger not found")

@app.post("/chargers", response_model=Charger, status_code=201)
def add_charger(data: AddCharger):
    for charger in chargers:
        if charger.id == data.id:
            raise HTTPException(status_code=409, detail="Charger already exists")

    charger = Charger(
        id=data.id,
        status="available",
        max_power_kw=data.max_power_kw,
        current_power_kw=0.0,
        energy_delivered_kwh="0.0",
    )

    chargers.append(charger)

    return charger
