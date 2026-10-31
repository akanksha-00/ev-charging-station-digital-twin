from turtle import title
from models import ChargerRecord
from schemas import Charger, AddCharger
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
