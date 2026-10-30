from typing import Literal

from pydantic import BaseModel, Field

class Charger(BaseModel):
    id: str
    status: Literal["available", "charging", "paused", "faulted"]
    max_power_kw: float=Field(gt=0)
    current_power_kw: float=Field(ge=0)
    energy_delivered_kwh: float=Field(ge=0)
    
class AddCharger(BaseModel):
    id: str=Field(min_length=1)
    max_power_kw: float=Field(gt=0)
    