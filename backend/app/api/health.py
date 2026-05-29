"""Health check endpoint."""
from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import async_session

router = APIRouter()


@router.get("/health")
async def health_check():
    """Verifica que la API y la base de datos respondan."""
    db_ok = False
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
