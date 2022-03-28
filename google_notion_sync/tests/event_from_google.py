# app to sync google calendar to notion calendar
# .env file contains notion database id
import os
import logging
import pickle


from dotenv import load_dotenv

from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service, google_calendar_sync_events_list 
from google_notion_sync.google_api.drive import get_google_drive_service
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.classes.event import Event
from google_notion_sync.utils.helpers import as_list

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./google_notion_sync/logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

def run():
    logger.info("NEW EXECUTION")
    load_dotenv()
    GOOGLE_DRIVE_FILE_ID = os.getenv('GOOGLE_DRIVE_FILE_ID')
    SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/drive']
    creds = get_google_creds(SCOPES, token_path='./google_notion_sync/config/token.json', credentials_path='./google_notion_sync/config/credentials.json')
    calendar_service = get_google_calendar_service(creds)
    drive_service = get_google_drive_service(creds)
    all_google_calendars = get_all_google_calendars(calendar_service)
    logger.info(all_google_calendars)
    all_google_events = []
    google_events = google_calendar_sync_events_list(calendar_service,drive_service,google_drive_fileId=GOOGLE_DRIVE_FILE_ID,
        calendar_id=all_google_calendars[0]['id'],resync=True,timeMinDays=1,timeMaxDays=10)
    logger.info(f"google_events:{google_events}")
    with open ("./google_notion_sync/data/11.pickle","wb") as f:
        pickle.dump(google_events,f)
    for event in google_events:
        ev = Event()
        ev.from_google_event(event)
        logger.warning(f"event = {event}")
        logger.warning(f"ev = {ev.properties}")
        

if __name__ == "__main__":
    run()