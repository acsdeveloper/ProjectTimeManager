from django.core.management.base import BaseCommand
from tasks.models import Task, WorkSession
import gspread
from google.oauth2.service_account import Credentials
from datetime import timedelta

class Command(BaseCommand):  # ✅ This must exist and be named exactly "Command"
    help = 'Exports accurate task time to Google Sheet'

    def handle(self, *args, **kwargs):
        data = []

        tasks = Task.objects.all()

        for task in tasks:
            sessions = WorkSession.objects.filter(task=task)
            total_seconds = sum((ws.duration.total_seconds() for ws in sessions if ws.duration), 0)
            time_spent = str(timedelta(seconds=total_seconds))

            data.append([task.user.username, task.title, time_spent])

        # Connect to Google Sheet
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("credentials/credentials.json", scopes=scope)
        client = gspread.authorize(creds)

        sheet = client.open_by_key("your-google-sheet-id").sheet1

        # Update Sheet
        sheet.update('A2', data)  # A2 assumes headers are in row 1

        self.stdout.write(self.style.SUCCESS("✅ Successfully exported to Google Sheet"))
