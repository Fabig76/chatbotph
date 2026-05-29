"""Hermes Agent — Async worker for background jobs (sync, email, etc.)."""
import asyncio
import logging
from datetime import datetime, timezone
from app.db.session import async_session
from app.services.sheets_sync import sync_residentes, sync_saldos

logger = logging.getLogger(__name__)

# Intervalos (en segundos)
SYNC_RESIDENTES_INTERVAL = 3600  # 1 hora
SYNC_SALDOS_INTERVAL = 1800      # 30 minutos


async def run_sync_residentes():
    """Sync residentes sheet every hour."""
    while True:
        try:
            async with async_session() as session:
                run = await sync_residentes(session)
                await session.commit()
                logger.info(
                    "Sync residentes completado",
                    extra={"rows": run.rows_total, "changed": run.rows_changed, "status": run.status},
                )
        except Exception as e:
            logger.error("Error en sync residentes", exc_info=e)
        await asyncio.sleep(SYNC_RESIDENTES_INTERVAL)


async def run_sync_saldos():
    """Sync saldos sheet every 30 minutes."""
    while True:
        try:
            async with async_session() as session:
                run = await sync_saldos(session)
                await session.commit()
                logger.info(
                    "Sync saldos completado",
                    extra={"rows": run.rows_total, "changed": run.rows_changed, "status": run.status},
                )
        except Exception as e:
            logger.error("Error en sync saldos", exc_info=e)
        await asyncio.sleep(SYNC_SALDOS_INTERVAL)


async def main():
    """Run all worker tasks concurrently."""
    logger.info("Hermes Agent Worker iniciado")
    await asyncio.gather(
        run_sync_residentes(),
        run_sync_saldos(),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    asyncio.run(main())
