"""Hermes Agent — Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    debug: bool = False
    # CORS
    cors_origins: list[str] = ["https://adminbot.info"]

    # Database
    database_url: str = "postgresql+asyncpg://hermes:hermes@db:5432/hermes"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Telegram
    telegram_bot_token: str = ""
    telegram_admin_chat_ids: List[int] = []
    telegram_porteria_chat_ids: List[int] = []

    # Google
    google_service_account_json: str = "./credentials/google-service-account.json"
    google_sheet_id: str = ""
    google_sheet_residentes_range: str = "Residentes!A:Z"
    google_sheet_saldos_range: str = "Saldos!A:Z"

    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # OTP
    otp_salt: str = "change-me-in-production"

    # Backups
    backup_dir: str = "/backups"
    backup_retention_days: int = 30

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
