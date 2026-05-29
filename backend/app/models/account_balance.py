"""account_balances — Caché de saldos por unidad sincronizado desde Sheets."""
from datetime import date, datetime
from sqlalchemy import ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class AccountBalance(TimestampMixin, Base):
    __tablename__ = "account_balances"

    unit_id: Mapped[UUID] = mapped_column(ForeignKey("units.id"), unique=True, nullable=False)
    balance_cop: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, comment="Saldo en pesos COP")
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, comment="Fecha de corte del contador")
    source_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    unit: Mapped["Unit"] = relationship(back_populates="balance")
