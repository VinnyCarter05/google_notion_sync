import logging
import os

from dotenv import load_dotenv

from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service
from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.drive import get_google_drive_service

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE = os.getenv('NOTION_DATABASE')
HEADERS = {"Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-02-22",
        }

logger.info(f"NOTION_DATABSE = {NOTION_DATABASE}")
GOOGLE_DRIVE_FILE_ID = os.getenv('GOOGLE_DRIVE_FILE_ID')
GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID = os.getenv('GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID')
SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/drive']
CREDS = get_google_creds(SCOPES, token_path='./google_notion_sync/config/token.json', credentials_path='./google_notion_sync/config/credentials.json')
CALENDAR_SERVICE = get_google_calendar_service(CREDS)
DRIVE_SERVICE = get_google_drive_service(CREDS)
ALL_GOOGLE_CALENDARS = get_all_google_calendars(CALENDAR_SERVICE)