"""Telegram webhook endpoint."""
import logging
from fastapi import APIRouter, Request, HTTPException
from telegram import Update
from app.services.telegram_bot import build_application

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Build once on import
_bot_app = None


def get_bot_app():
    global _bot_app
    if _bot_app is None:
        _bot_app = build_application()
    return _bot_app


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive Telegram updates via webhook."""
    app = get_bot_app()
    try:
        body = await request.json()
        update = Update.de_json(body, app.bot)
        await app.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.error("Error processing Telegram update", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhook/info")
async def webhook_info():
    """Get current webhook status."""
    app = get_bot_app()
    wh = await app.bot.get_webhook_info()
    return {
        "url": wh.url,
        "has_custom_certificate": wh.has_custom_certificate,
        "pending_update_count": wh.pending_update_count,
        "max_connections": wh.max_connections,
    }
