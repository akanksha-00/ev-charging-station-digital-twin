from turtle import title
from uuid import UUID
from models import ChargerRecord, ChargingSessionRecord
from schemas import Charger, AddCharger, ChargingSession, CreateChargingSession
from psycopg.errors import UniqueViolation
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from database import get_db

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
def get_chargers(db: Session = Depends(get_db)):
    query = select(ChargerRecord).order_by(ChargerRecord.id)
    return db.scalars(query).all()


@app.get("/chargers/{charger_id}", response_model=Charger)
def get_charger_by_id(charger_id: str, db: Session = Depends(get_db)):
    charger = db.get(ChargerRecord, charger_id)

    if charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")

    return charger


@app.post("/chargers", response_model=Charger, status_code=201)
def add_charger(data: AddCharger, db: Session = Depends(get_db)):

    charger = ChargerRecord(
        id=data.id,
        max_power_kw=data.max_power_kw,
    )

    db.add(charger)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        if isinstance(error.orig, UniqueViolation):
            raise HTTPException(
                status_code=409, detail="Charger ID already exists"
            ) from error

        raise

    db.refresh(charger)
    return charger


@app.post("/sessions", response_model=ChargingSession, status_code=201)
def start_charging_session(data: CreateChargingSession, db: Session = Depends(get_db)):
    query = (
        select(ChargerRecord)
        .where(ChargerRecord.id == data.charger_id)
        .with_for_update()
    )

    charger = db.scalar(query)
    if charger is None:
        raise HTTPException(
            status_code=404,
            detail="Charger not found",
        )
    if charger.status != "available":
        raise HTTPException(
            status_code=409,
            detail="Charger is not available",
        )

    charging_session = ChargingSessionRecord(
        charger_id=data.charger_id,
        target_energy_kwh=data.target_energy_kwh,
    )

    charger.status = "charging"

    db.add(charging_session)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        if (
            isinstance(error.orig, UniqueViolation)
            and error.orig.diag.constraint_name == "unique_session_active_per_charger"
        ):
            raise HTTPException(
                status_code=409, detail="Charger already has an active session"
            ) from error

        raise

    db.refresh(charging_session)
    return charging_session


@app.get("/session/{session_id}", response_model=ChargingSession, status_code=200)
def get_session(session_id: UUID, db: Session = Depends(get_db)):

    charging_session = db.get(ChargingSessionRecord(), session_id)

    if charging_session is None:
        raise HTTPException(
            status_code=404,
            detail="Charging Session not found",
        )
        
    return charging_session
