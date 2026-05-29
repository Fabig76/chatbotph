"""admin_chats — Whitelist de chat_ids de Telegram autorizados."""
from sqlalchemy import Boolean, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class AdminChat(TimestampMixin, Base):
    __tablename__ = "admin_chats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str | None] = mapped_column(String(20), comment="admin | portero")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
