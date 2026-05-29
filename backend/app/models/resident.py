"""residents — Réplica operativa desde Google Sheets (fuente de verdad)."""
from sqlalchemy import Boolean, ForeignKey, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Resident(TimestampMixin, Base):
    __tablename__ = "residents"

    unit_id: Mapped[UUID] = mapped_column(ForeignKey("units.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    document_id_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="SHA-256; nunca en claro")
    document_id_last4: Mapped[str | None] = mapped_column(String(4), comment="Últimos 4 dígitos para mostrar")
    email: Mapped[str | None] = mapped_column(String(255), comment="Cifrado en reposo si es viable")
    phone: Mapped[str | None] = mapped_column(String(20), comment="E.164")
    is_owner: Mapped[bool | None] = mapped_column(Boolean, comment="Propietario o residente")
    sheet_row_hash: Mapped[str | None] = mapped_column(String(64), comment="Hash del registro para detectar cambios")
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="Última vez que coincidió con Sheets")

    # Relationships
    unit: Mapped["Unit"] = relationship(back_populates="residents")
