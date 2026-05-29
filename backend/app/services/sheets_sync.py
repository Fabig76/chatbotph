"""Google Sheets — read residentes and saldos."""
import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.google_auth import get_sheets_service
from app.models.unit import Unit
from app.models.resident import Resident
from app.models.account_balance import AccountBalance
from app.models.sheet_sync_run import SheetSyncRun
from app.core.config import settings


def _read_sheet_range(spreadsheet_id: str, range_name: str) -> list[list[str]]:
    """Read a range from Google Sheets. Returns rows as lists of strings."""
    service = get_sheets_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])


def _row_hash(row: list) -> str:
    """SHA-256 hash of a row for change detection."""
    return hashlib.sha256(json.dumps(row, default=str).encode()).hexdigest()


async def sync_residentes(session: AsyncSession, sheet_id: str | None = None) -> SheetSyncRun:
    """Sync 'Residentes' sheet → units + residents tables."""
    sid = sheet_id or settings.google_sheet_id
    run = SheetSyncRun(sheet_id=sid, started_at=datetime.now(timezone.utc), status="running")
    session.add(run)
    await session.flush()

    try:
        rows = _read_sheet_range(sid, settings.google_sheet_residentes_range)
        if not rows or len(rows) < 2:
            raise ValueError("Sheet vacía o sin encabezados")

        headers = [h.strip().lower() for h in rows[0]]
        data_rows = rows[1:]

        changed = 0
        for row in data_rows:
            if len(row) < len(headers):
                continue
            row_data = dict(zip(headers, row))

            unit_code = row_data.get("unidad", row_data.get("code", "")).strip()
            if not unit_code:
                continue

            # Upsert unit
            stmt = select(Unit).where(Unit.code == unit_code)
            unit = (await session.execute(stmt)).scalar_one_or_none()
            if not unit:
                unit = Unit(code=unit_code, kind=row_data.get("tipo", "apartment"))
                session.add(unit)
                await session.flush()

            # Hash for change detection
            rh = _row_hash(row)

            # Check if resident already exists
            full_name = row_data.get("nombre", row_data.get("full_name", "")).strip()
            email = row_data.get("email", "").strip()
            phone = row_data.get("telefono", row_data.get("phone", "")).strip()

            stmt_r = select(Resident).where(
                Resident.unit_id == unit.id,
                Resident.full_name == full_name,
            )
            resident = (await session.execute(stmt_r)).scalar_one_or_none()

            if resident and resident.sheet_row_hash == rh:
                continue  # unchanged

            doc_id = row_data.get("documento", row_data.get("document_id", "")).strip()
            doc_hash = hashlib.sha256(doc_id.encode()).hexdigest() if doc_id else ""
            doc_last4 = doc_id[-4:] if len(doc_id) >= 4 else ""

            is_owner_str = row_data.get("propietario", row_data.get("is_owner", "si")).strip().lower()
            is_owner = is_owner_str in ("si", "s", "true", "1", "yes")

            if resident:
                resident.document_id_hash = doc_hash
                resident.document_id_last4 = doc_last4
                resident.email = email
                resident.phone = phone
                resident.is_owner = is_owner
                resident.sheet_row_hash = rh
                resident.synced_at = datetime.now(timezone.utc)
            else:
                resident = Resident(
                    unit_id=unit.id,
                    full_name=full_name,
                    document_id_hash=doc_hash,
                    document_id_last4=doc_last4,
                    email=email,
                    phone=phone,
                    is_owner=is_owner,
                    sheet_row_hash=rh,
                    synced_at=datetime.now(timezone.utc),
                )
                session.add(resident)

            changed += 1

        await session.flush()
        run.status = "success"
        run.finished_at = datetime.now(timezone.utc)
        run.rows_total = len(data_rows)
        run.rows_changed = changed

    except Exception as e:
        run.status = "error"
        run.finished_at = datetime.now(timezone.utc)
        run.error = str(e)
        await session.flush()

    return run


async def sync_saldos(session: AsyncSession, sheet_id: str | None = None) -> SheetSyncRun:
    """Sync 'Saldos' sheet → account_balances table."""
    sid = sheet_id or settings.google_sheet_id
    run = SheetSyncRun(sheet_id=sid, started_at=datetime.now(timezone.utc), status="running")
    session.add(run)
    await session.flush()

    try:
        rows = _read_sheet_range(sid, settings.google_sheet_saldos_range)
        if not rows or len(rows) < 2:
            raise ValueError("Sheet vacía o sin encabezados")

        headers = [h.strip().lower() for h in rows[0]]
        data_rows = rows[1:]

        changed = 0
        for row in data_rows:
            if len(row) < len(headers):
                continue
            row_data = dict(zip(headers, row))

            unit_code = row_data.get("unidad", row_data.get("code", "")).strip()
            if not unit_code:
                continue

            # Find unit
            stmt = select(Unit).where(Unit.code == unit_code)
            unit = (await session.execute(stmt)).scalar_one_or_none()
            if not unit:
                continue

            balance_str = row_data.get("saldo", row_data.get("balance", "0")).strip()
            balance_cop = Decimal(balance_str.replace("$", "").replace(".", "").replace(",", ".").strip() or "0")

            as_of_date_str = row_data.get("fecha_corte", row_data.get("as_of_date", "")).strip()
            try:
                as_of_date = date.fromisoformat(as_of_date_str)
            except (ValueError, TypeError):
                as_of_date = date.today()

            # Upsert balance
            stmt_b = select(AccountBalance).where(AccountBalance.unit_id == unit.id)
            balance = (await session.execute(stmt_b)).scalar_one_or_none()

            if balance:
                balance.balance_cop = balance_cop
                balance.as_of_date = as_of_date
                balance.source_updated_at = datetime.now(timezone.utc)
                balance.synced_at = datetime.now(timezone.utc)
            else:
                balance = AccountBalance(
                    unit_id=unit.id,
                    balance_cop=balance_cop,
                    as_of_date=as_of_date,
                    source_updated_at=datetime.now(timezone.utc),
                    synced_at=datetime.now(timezone.utc),
                )
                session.add(balance)

            changed += 1

        await session.flush()
        run.status = "success"
        run.finished_at = datetime.now(timezone.utc)
        run.rows_total = len(data_rows)
        run.rows_changed = changed

    except Exception as e:
        run.status = "error"
        run.finished_at = datetime.now(timezone.utc)
        run.error = str(e)
        await session.flush()

    return run
