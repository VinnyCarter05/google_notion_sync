# app to sync google calendar to notion calendar
# .env file contains notion database id
import pickle
import os
import logging

from dotenv import load_dotenv

# from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service 
from google_notion_sync.google_api.drive import get_google_drive_service
from google_notion_sync.classes.calendar import Calendar

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

def run():
    load_dotenv()
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    NOTION_DATABASE = os.getenv('NOTION_DATABASE')
    logger.info(f"NOTION_DATABSE = {NOTION_DATABASE}")
    GOOGLE_DRIVE_FILE_ID = os.getenv('GOOGLE_DRIVE_FILE_ID')
    SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/drive']
    creds = get_google_creds(SCOPES, token_path='./google_notion_sync/config/token.json', credentials_path='./google_notion_sync/config/credentials.json')
    calendar_service = get_google_calendar_service(creds)
    drive_service = get_google_drive_service(creds)
    notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, googleCalendarId="", NOTION_API_KEY=NOTION_API_KEY, calendarService=calendar_service, driveService=drive_service
        , googleDriveFileId=GOOGLE_DRIVE_FILE_ID, loadFrom = "notion", resync=True,timeMinDays=1,timeMaxDays=10)
    for event in notion_calendar.all_events:
        logger.warning(f"event = {event.properties}")
    with open ("./google_notion_sync/data/notion_calendar.pickle","wb") as f:
        pickle.dump(notion_calendar,f)
    
    # all_google_calendars = get_all_google_calendars(calendar_service)
    # currentGoogleCalendar = Calendar(notion_database_id=NOTION_DATABASE, googleCalendarId=all_google_calendars[0],calendarService=calendar_service, 
    #     driveService=drive_service,googleDriveFileId=GOOGLE_DRIVE_FILE_ID, loadFrom = "google", resync=True, timeMinDays=1, timeMaxDays=10)
    # print (all_google_calendars)
    # for event in currentGoogleCalendar.all_events:
    #     print (event.properties)

if __name__ == "__main__":
    run()