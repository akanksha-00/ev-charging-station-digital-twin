# Database models

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ChargerRecord(Base):
    __tablename__ = "chargers"

    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(default="available")
    max_power_kw: Mapped[float] = mapped_column()
    current_power_kw: Mapped[float] = mapped_column(default=0.0)
    energy_delivered_kwh: Mapped[float] = mapped_column(default=0.0)


class ChargingSessionRecord(Base):
    __tablename__ = "charging_sessions"

    __table_args__ = (
        CheckConstraint(
            "target_energy_kwh > 0",
            name="ck_sessions_target_energy_positive",
        ),
        CheckConstraint(
            "energy_delivered_kwh >= 0",
            name="ck_sessions_energy_delivered_non_negative",
        ),
        CheckConstraint(
            "status IN ('active','completed','stopped')",
            name="ck_session_status",
        ),
        Index(
            "unique_session_active_per_charger",
            "charger_id",
            unique=True,
            postgresql_where=text("status='active'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    charger_id: Mapped[str] = mapped_column(
        ForeignKey("chargers.id"),
        index=True,
    )
    status: Mapped[str] = mapped_column(
        default="active",
    )
    target_energy_kwh: Mapped[float] = mapped_column()
    energy_delivered_kwh: Mapped[float] = mapped_column(
        default=0.0,
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
