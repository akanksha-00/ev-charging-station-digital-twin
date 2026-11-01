# API schema

from datetime import datetime
from typing import Literal
from unittest.mock import Base
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class Charger(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: Literal["available", "charging", "paused", "faulted"]
    max_power_kw: float = Field(gt=0)
    current_power_kw: float = Field(ge=0)
    energy_delivered_kwh: float = Field(ge=0)


class AddCharger(BaseModel):
    id: str = Field(min_length=1)
    max_power_kw: float = Field(gt=0)


class ChargingSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    charger_id: str
    status: Literal["active", "completed", "stopped"]
    target_energy_kwh: float
    energy_delivered_kwh: float
    start_time: datetime
    end_time: datetime | None


class CreateChargingSession(BaseModel):
    charger_id: str = Field(min_length=1)
    target_energy_kwh: float = Field(gt=0)
