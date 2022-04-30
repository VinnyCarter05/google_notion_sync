import asyncio
from copy import deepcopy
import logging
from tokenize import Name
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.google_api.calendar import get_all_google_calendars, google_calendar_sync_events_list
from google_notion_sync.google_api.drive import google_drive_download_file, google_drive_replace_file

from google_notion_sync.notion_api.database import async_notion_update_pages

from google_notion_sync.utils.configure import ALL_GOOGLE_CALENDARS, ALL_GOOGLE_CALENDARS_DICT, CALENDAR_SERVICE, DRIVE_SERVICE, GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID, HEADERS, NOTION_API_KEY, NOTION_DATABASE
from google_notion_sync.utils.helpers import as_list, pickle_load, pickle_save

logger = logging.getLogger(__name__)

def update_notion_database (new_google_events):
    notion_calendar = Calendar(notion_database_id=NOTION_DATABASE,  NOTION_API_KEY=NOTION_API_KEY)
    logger.info (f"updating notion_calendar = {notion_calendar}")
    new_calendar = Calendar(google_events=new_google_events, all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
    logger.info (f"adding new_calendar = {new_calendar}")
    merged_calendar = deepcopy(notion_calendar)
    merged_calendar.add_calendar(new_calendar=new_calendar)
    asyncio.run(async_notion_update_pages(NOTION_DATABASE, headers=HEADERS, events = [event for event in merged_calendar.all_events]))

def get_all_google_events():
    all_google_events = []
    for google_calendar in ALL_GOOGLE_CALENDARS:
        google_events = google_calendar_sync_events_list(CALENDAR_SERVICE,DRIVE_SERVICE,google_drive_fileId=GOOGLE_DRIVE_FILE_ID,
            calendar_id=google_calendar['id'],resync=True, timeMinDays=None, timeMaxDays=None)
        logger.info (f"google_events = {google_events}")
        all_google_events.extend(as_list(google_events))
    logger.debug(f"all_google_events = {all_google_events}")
    return all_google_events

def get_all_new_google_events():
    all_google_events = []
    for google_calendar in ALL_GOOGLE_CALENDARS:
        google_events = google_calendar_sync_events_list(CALENDAR_SERVICE,DRIVE_SERVICE,google_drive_fileId=GOOGLE_DRIVE_FILE_ID,
            calendar_id=google_calendar['id'],resync=False, timeMinDays=None, timeMaxDays=None)
        logger.info (f"google_events = {google_events}")
        all_google_events.extend(as_list(google_events))
    logger.debug(f"all_google_events = {all_google_events}")
    return all_google_events

def calendar_save_to_google_drive(calendar):
    pickle_file_path = "./google_notion_sync/data/current_calendar.pickle"
    pickle_save(calendar,pickle_file_path)
    google_drive_replace_file(service=DRIVE_SERVICE, file_name=pickle_file_path, fileId=GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID,mimetype="application/octet-stream")

def calendar_load_from_google_drive():
    pickle_file_path = "./google_notion_sync/data/current_calendar.pickle"
    google_drive_download_file(service=DRIVE_SERVICE, file_name=pickle_file_path, fileId=GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID)
    return (pickle_load(pickle_file_path))
    

if __name__ == "__main__":
    calendar_db = Calendar()
    notion_calendar = Calendar()
    while True:
        try:
            print("1. resync all google calendar events\n2. download new google calendar events\n3. upload calendar to google drive\n4. download calendar from google drive")
            print("5. print calendar\n6. download all notion events")
            choice = int(input("10. exit\n"))
        except ValueError:
            print ("\nInteger value please. 5 to exit\n")
            continue
        match choice:
            case 1:
                calendar_db = Calendar(google_events=get_all_google_events(), all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
            case 2:
                calendar_db = Calendar(google_events=get_all_new_google_events(),all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
            case 3:
                calendar_save_to_google_drive(calendar_db)
            case 4:
                calendar_db = calendar_load_from_google_drive()
            case 5:
                print (f"calendar_db = {calendar_db}")
                print (f"notion_calendar = {notion_calendar}")
            case 6:
                notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
            case 10:
                break
            case _:
                print (choice)
            
