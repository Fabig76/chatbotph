"""Telegram bot service — webhook handler, commands, and messages."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.core.config import settings
from app.models.unit import Unit
from app.models.account_balance import AccountBalance
from app.models.admin_chat import AdminChat

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────

def _format_cop(value: Decimal) -> str:
    """Format a number as Colombian pesos: $ 1.234.567"""
    if value is None:
        return "$ 0"
    whole = int(abs(value))
    formatted = f"{whole:,}".replace(",", ".")
    sign = "-" if value < 0 else ""
    return f"{sign}$ {formatted}"


async def _is_authorized(chat_id: int, session: AsyncSession) -> bool:
    """Check if a chat_id is in the admin whitelist."""
    stmt = select(AdminChat).where(
        AdminChat.chat_id == chat_id,
        AdminChat.active == True,
    )
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def _get_unit_balance(unit_code: str, session: AsyncSession) -> dict | None:
    """Look up a unit by code and return its balance info."""
    stmt = select(Unit).where(Unit.code.ilike(f"%{unit_code}%"))
    unit = (await session.execute(stmt)).scalar_one_or_none()
    if not unit:
        return None

    stmt_b = select(AccountBalance).where(AccountBalance.unit_id == unit.id)
    balance = (await session.execute(stmt_b)).scalar_one_or_none()

    return {
        "unit": unit,
        "balance": balance,
    }


# ── Command Handlers ─────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    async with async_session() as session:
        authorized = await _is_authorized(chat_id, session)

    if not authorized:
        await update.message.reply_text(
            "⛔ No estás autorizado para usar este bot.\n"
            "Si eres el administrador, solicita que agreguen tu chat_id."
        )
        return

    await update.message.reply_text(
        "🤖 *Hermes Agent — Administración*\n\n"
        "Comandos disponibles:\n\n"
        "`/saldo <código>` — Consulta el saldo de una unidad\n"
        "  Ej: `/saldo T1-301`\n\n"
        "`/start` — Muestra este mensaje",
        parse_mode="Markdown",
    )


async def cmd_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /saldo <unit_code> command."""
    chat_id = update.effective_chat.id

    async with async_session() as session:
        authorized = await _is_authorized(chat_id, session)
        if not authorized:
            await update.message.reply_text("⛔ No estás autorizado.")
            return

        if not context.args:
            await update.message.reply_text(
                "ℹ️ Usa: /saldo <código de unidad>\n"
                "Ej: `/saldo T1-301`",
                parse_mode="Markdown",
            )
            return

        unit_code = " ".join(context.args).strip()
        result = await _get_unit_balance(unit_code, session)

    if not result:
        await update.message.reply_text(
            f"❌ No encontré ninguna unidad que coincida con \"{unit_code}\".\n"
            "Verifica el código e intenta de nuevo."
        )
        return

    unit = result["unit"]
    balance = result["balance"]

    if balance is None:
        msg = (
            f"🏠 *{unit.code}*\n\n"
            "📊 *Saldo:* No disponible\n"
            "No hay datos de saldo sincronizados para esta unidad."
        )
    else:
        msg = (
            f"🏠 *{unit.code}*\n\n"
            f"📊 *Saldo:* {_format_cop(balance.balance_cop)}\n"
            f"📅 *Corte:* {balance.as_of_date}\n"
            f"🔄 *Actualizado:* {balance.synced_at.strftime('%d/%m/%Y %H:%M') if balance.synced_at else 'N/A'}"
        )

        # Add warning if balance is not zero (paz y salvo no disponible)
        if balance.balance_cop != 0:
            msg += "\n\n⚠️ *Saldo pendiente* — Paz y salvo no disponible"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias de /start."""
    await cmd_start(update, context)


# ── Error Handler ────────────────────────────────────────────────

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error("Update %s caused error %s", update, context.error)


# ── Application Factory ──────────────────────────────────────────

def build_application() -> Application:
    """Build the Telegram bot Application with all handlers."""
    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("saldo", cmd_saldo))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_error_handler(error_handler)

    return app
