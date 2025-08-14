from django.shortcuts import redirect

def frontend_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'frontend_user_id' not in request.session:
            return redirect('frontend_login')
        return view_func(request, *args, **kwargs)
    return wrapper


import os
import gspread
from google.oauth2.service_account import Credentials

# Setup credentials path
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = r'C:\Users\devsk\OneDrive\Desktop\CRUD\TaskManager\credentials\credentials.json'  # ✅ Your real file





SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



# utils.py

def format_seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# def send_data_to_google_sheet(rows, sheet_id, worksheet_name='Sheet1'):
#     creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     client = gspread.authorize(creds)
#     sheet = client.open_by_key(sheet_id)

#     print("📋 Available Worksheets:", [ws.title for ws in sheet.worksheets()])

#     try:
#         worksheet = sheet.worksheet(worksheet_name)
#     except gspread.exceptions.WorksheetNotFound:
#         print(f"🛠️ Worksheet '{worksheet_name}' not found. Creating it...")
#         worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

#     print(f"✏️ Writing to worksheet: {worksheet.title}")
#     worksheet.clear()

#     # Header row
#     worksheet.append_row([
#         "Username", "Task Title", "Description", "Created At", "Deadline",
#         "Paused", "Resumed", "Submitted At", "Status", "Total Time Tracked"
#     ])
import os
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = r'C:\Users\devsk\OneDrive\Desktop\CRUD\TaskManager\credentials\credentials.json'  # ✅ Your real file

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def send_data_to_google_sheet(rows, sheet_id, worksheet_name='Sheet1'):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)

    try:
        worksheet = sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

    worksheet.clear()

    # Headers
    worksheet.append_row([
        "Username", "Task Title", "Description", "Created At", "Deadline",
        "Paused", "Resumed", "Submitted At", "Status", "Total Time Tracked"
    ])

    if not rows:
        print("⚠️ No rows to export.")
        return

    worksheet.append_rows(rows)  # ✅ More efficient than row-by-row

    print(f"✅ Exported {len(rows)} row(s) to Google Sheet.")

