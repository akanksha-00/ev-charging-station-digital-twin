from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class ChargerRecord(Base):
    __tablename__ = "chargers"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(default="available")
    max_power_kw: Mapped[float] = mapped_column()
    current_power_kw: Mapped[float] = mapped_column(default=0.0)
    energy_delivered_kwh: Mapped[float] = mapped_column(default=0.0)
    