#!/usr/bin/env python3
"""
Test connection to Google Sheets for Hermes Agent.

Usage:
    python scripts/test_sheets.py

Requires:
    - Google service account JSON in ./credentials/google-service-account.json
    - Sheet shared with the service account email
"""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.google_auth import get_sheets_service


def main():
    creds_path = Path("credentials/google-service-account.json")
    if not creds_path.exists():
        print(f"❌ Service account key not found: {creds_path}")
        print("")
        print("Para crear una cuenta de servicio:")
        print("1. Ve a https://console.cloud.google.com/apis/credentials")
        print("2. Crea una cuenta de servicio (Service Account)")
        print("3. Genera una clave JSON y guárdala en credentials/")
        print("4. Comparte la Sheet con el email de la cuenta de servicio")
        return 1

    try:
        service = get_sheets_service()
        sheets = service.spreadsheets()
        print("✅ Conexión Google Sheets establecida")

        # Try to read the configured sheet
        from app.core.config import settings
        if settings.google_sheet_id:
            result = sheets.values().get(
                spreadsheetId=settings.google_sheet_id,
                range="A1:Z1",
            ).execute()
            values = result.get("values", [])
            if values:
                print(f"✅ Sheet encontrada. Headers: {values[0]}")
            else:
                print("⚠️ Sheet encontrada pero vacía")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
