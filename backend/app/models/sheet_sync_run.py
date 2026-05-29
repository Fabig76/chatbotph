"""sheet_sync_runs — Auditoría de cada corrida de sincronización."""
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class SheetSyncRun(TimestampMixin, Base):
    __tablename__ = "sheet_sync_runs"

    sheet_id: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows_total: Mapped[int | None] = mapped_column(Integer)
    rows_changed: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(20), comment="success | error")
    error: Mapped[str | None] = mapped_column(Text)
