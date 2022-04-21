# app to sync google calendar to notion calendar
# .env file contains notion database id
import os
import logging
import pickle

from dotenv import load_dotenv

# from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service, google_calendar_sync_events_list 
from google_notion_sync.google_api.drive import get_google_drive_service
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.utils.configure import CALENDAR_SERVICE, DRIVE_SERVICE, GOOGLE_DRIVE_FILE_ID
from google_notion_sync.utils.helpers import as_list

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

def run():
    all_google_calendars = get_all_google_calendars(CALENDAR_SERVICE)
    logger.info(all_google_calendars)
    all_google_events = []
    for i in range(len(all_google_calendars)):
        google_events = google_calendar_sync_events_list(CALENDAR_SERVICE,DRIVE_SERVICE,google_drive_fileId=GOOGLE_DRIVE_FILE_ID,
            calendar_id=all_google_calendars[i]['id'],resync=True, timeMinDays=None, timeMaxDays=None)
        logger.info (f"google_events = {google_events}")
        all_google_events.extend(as_list(google_events))
    logger.debug(f"all_google_events = {all_google_events}")
    with open ("./google_notion_sync/data/all_google_events.pickle","wb") as f:
        pickle.dump(all_google_events, f)


if __name__ == "__main__":
    run()