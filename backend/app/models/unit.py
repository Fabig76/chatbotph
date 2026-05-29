"""units — Unidades físicas del conjunto (apartamentos, casas)."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Unit(TimestampMixin, Base):
    __tablename__ = "units"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="Ej: Torre 1 - Apto 301")
    kind: Mapped[str | None] = mapped_column(String(20), comment="apartment | house")

    # Relationships
    residents: Mapped[list["Resident"]] = relationship(back_populates="unit")
    balance: Mapped["AccountBalance | None"] = relationship(back_populates="unit", uselist=False)
