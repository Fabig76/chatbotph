"""Google Workspace authentication — Service Account."""
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_credentials():
    """Load Google service account credentials from JSON file."""
    creds_path = Path(settings.google_service_account_json)
    if not creds_path.exists():
        raise FileNotFoundError(f"Service account key not found: {creds_path}")
    return service_account.Credentials.from_service_account_file(
        str(creds_path), scopes=SCOPES
    )


def get_sheets_service():
    """Build and return a Google Sheets API service client."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def get_gmail_service():
    """Build and return a Gmail API service client."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def get_calendar_service():
    """Build and return a Google Calendar API service client."""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)
