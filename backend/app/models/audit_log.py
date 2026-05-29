"""audit_log — Cambios sensibles. Append-only."""
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_log"

    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor_kind: Mapped[str] = mapped_column(String(20), comment="admin | resident | system")
    actor_id: Mapped[str | None] = mapped_column(String(100), comment="chat_id, resident_id o 'system'")
    action: Mapped[str] = mapped_column(String(100), comment="Ej: request.approve, paz_y_salvo.issue")
    target_kind: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(100))
    details_json: Mapped[dict | None] = mapped_column(JSONB)
