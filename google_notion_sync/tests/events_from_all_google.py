# app to sync google calendar to notion calendar
# .env file contains notion database id
import os
import logging
import pickle


from dotenv import load_dotenv

from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service, get_google_instances, google_calendar_sync_events_list
from google_notion_sync.google_api.drive import get_google_drive_service, google_drive_file_upload, google_drive_replace_file
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.classes.event import Event
from google_notion_sync.utils.helpers import as_list, pickle_load, pickle_save

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)


def run():
    all_google_calendar_events = pickle_load("./google_notion_sync/data/all_google_events.pickle")
    logger.info("NEW EXECUTION")
    load_dotenv()
    GOOGLE_DRIVE_FILE_ID = os.getenv('GOOGLE_DRIVE_FILE_ID')
    GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID = os.getenv('GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID')
    SCOPES = ['https://www.googleapis.com/auth/calendar',
              'https://www.googleapis.com/auth/drive']
    creds = get_google_creds(SCOPES, token_path='./google_notion_sync/config/token.json',
                             credentials_path='./google_notion_sync/config/credentials.json')
    calendar_service = get_google_calendar_service(creds)
    drive_service = get_google_drive_service(creds)
    all_google_calendars = get_all_google_calendars(calendar_service)
    logger.info(all_google_calendars)
    all_google_events = []
    google_calendar = Calendar(google_events=all_google_calendar_events, all_google_calendars=all_google_calendars)
    # google_calendar.from_google_calendar_events(all_google_calendar_events)
    # google_calendar.sort_events_by_start_date()
    print (google_calendar)
    pickle_file_path = "./google_notion_sync/data/google_calendar.pickle"
    pickle_save(google_calendar,pickle_file_path)
    google_drive_replace_file(drive_service,pickle_file_path, GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID,"application/octet-stream")
    
    # for event in all_google_calendar_events:  # google_instances:
    #     ev = Event(google_event=event)
    #     all_google_events.append(ev)
    #     logger.warning(f"event = {event}")
    #     logger.warning(f"ev = {ev.properties}")
    # print (all_google_events[0:10])
    # logger.warning(f"nextSyncToken = {nextSyncToken}")


if __name__ == "__main__":
    run()
