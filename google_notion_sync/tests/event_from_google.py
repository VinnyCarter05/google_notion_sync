# app to sync google calendar to notion calendar
# .env file contains notion database id
import os
import logging
import pickle


from dotenv import load_dotenv

from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service, get_google_instances, google_calendar_sync_events_list 
from google_notion_sync.google_api.drive import get_google_drive_service
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.classes.event import Event
from google_notion_sync.utils.helpers import as_list

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./google_notion_sync/logs/example.log', filemode='w')
# logger = logging.getLogger(__name__)

def new_raw_events(pickle_file_name="example.pickle"):
    pickle_file_path = os.path.join("./google_notion_sync/data", pickle_file_name)
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
        calendar_id=all_google_calendars[0]['id'],resync=False)#,timeMinDays=10,timeMaxDays=30)
    logger.info(f"google_events:{google_events}")
    # google_instances = []
    # for num, google_trial_event in enumerate(google_events):
    #     logger.warning (f"{num}, {google_trial_event}")
    #     try:
    #         google_instance, nextSyncToken = get_google_instances(calendar_service,google_trial_event['calendar'], google_trial_event['id'])
    #         google_instances.extend(google_instance)
    #         logger.warning (f"{num} non-recurring: {google_instances[-1]}")
    #     except:
    #         logger.warning (f"{num} error non-recurring: {google_trial_event}")
    with open (pickle_file_path,"wb") as f:
        pickle.dump(google_events,f)
    for event in google_events:#google_instances:
        ev = Event()
        ev.from_google_event(event)
        logger.warning(f"event = {event}")
        logger.warning(f"ev = {ev.properties}")
    # logger.warning(f"nextSyncToken = {nextSyncToken}")

if __name__ == "__main__":
    file_name = "abc"
    log_file_path = os.path.join("./logs", file_name+".log")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename=log_file_path, filemode='w')
    logger = logging.getLogger(__name__)
    pickle_file_name = file_name+".pickle"
    new_raw_events(pickle_file_name)