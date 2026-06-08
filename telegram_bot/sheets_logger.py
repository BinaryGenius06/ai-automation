import os, json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheets_service():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON not set in .env")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def log_lead(name: str, business: str, problem: str, email: str,
             score: str, reason: str, confidence: str) -> bool:
    """
    Append lead row to correct Sheet tab.
    Returns True on success, False on failure — never crashes bot.
    """
    try:
        service = get_sheets_service()
        sheet_name = "Hot Leads" if score == "hot" else "Cold Leads"
        row = [[
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name, business, problem, email,
            score.upper(), reason, confidence
        ]]
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A:H",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()
        return True
    except Exception as e:
        print(f"Sheets logging failed: {e}")
        return False


if __name__ == "__main__":
    result = log_lead(
        name="Test User", business="Test Co",
        problem="test problem", email="test@test.com",
        score="hot", reason="test entry", confidence="high"
    )
    print("Logged:", result)