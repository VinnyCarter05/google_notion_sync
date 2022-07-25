import asyncio
from copy import deepcopy
import logging
from tokenize import Name
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.google_api.calendar import get_all_google_calendars, google_calendar_sync_events_list
from google_notion_sync.google_api.drive import google_drive_download_file, google_drive_replace_file

from google_notion_sync.notion_api.database import async_notion_update_pages

from google_notion_sync.utils.configure import ALL_GOOGLE_CALENDARS, ALL_GOOGLE_CALENDARS_DICT, CALENDAR_SERVICE, DRIVE_SERVICE, GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_GOOGLE_CALENDAR_FILE_ID, HEADERS, NOTION_API_KEY, NOTION_DATABASE
from google_notion_sync.utils.helpers import as_list, datetime_from_now, event_start_datetime, pickle_load, pickle_save

logger = logging.getLogger(__name__)

def update_notion_database (new_google_events):
    notion_calendar = Calendar(notion_database_id=NOTION_DATABASE,  NOTION_API_KEY=NOTION_API_KEY)
    logger.info (f"updating notion_calendar = {notion_calendar}")
    new_calendar = Calendar(google_events=new_google_events, all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
    logger.info (f"adding new_calendar = {new_calendar}")
    merged_calendar = deepcopy(notion_calendar)
    merged_calendar.add_calendar(new_calendar=new_calendar)
    asyncio.run(async_notion_update_pages(NOTION_DATABASE, headers=HEADERS, events = [event for event in merged_calendar.all_events]))

def notion_update_pages(NOTION_DATABASE, new_calendar, start_days_from_now=36500, end_days_from_now=-36500):
    events = [event for event in new_calendar.all_events if (datetime_from_now(start_days_from_now) < event_start_datetime(event=event) and datetime_from_now(end_days_from_now) > event_start_datetime(event))]
    logger.info (f"events to upload = {events}")
    asyncio.run(async_notion_update_pages(NOTION_DATABASE=NOTION_DATABASE, headers=HEADERS, events=events))

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
    new_calendar = Calendar()
    current_calendar = Calendar()
    notion_calendar = Calendar()
    start_days_from_now, end_days_from_now = -36500, 36500
    start_date = datetime_from_now(-36500)
    end_date = datetime_from_now(36500)
    while True:
        try:
            print("0. do resync from google calendar from today for 365 days")
            print("1. resync all google calendar events to new events")
            print("2. download new google calendar events to new events")
            print("3. upload current calendar to google drive")
            print("4. download calendar from google drive to current calendar")
            print("5. print calendars")
            print("6. download all notion events to notion calendar")
            print("7. merge new events to notion calendar")
            print("8. merge new events to current calendar")
            print("9. merge notion calendar to current calendar")
            print("10. clear new events")
            print("11. clear current calendar")
            print("12. clear notion calendar")
            print("20. delete notion (online) calendar between dates")
            print("21. upload current calendar to notion between dates")
            print("30. set start date by number")
            print("31. set end date by number")
            print("77. new resync google calendar to notion from today for 365 days")
            choice = int(input("99. exit\n"))
        except ValueError:
            print ("\nInteger value please. 99 to exit\n")
            continue
        match choice:
            case 0:
                #1
                print("loading google calendars")
                new_calendar = Calendar(google_events=get_all_google_events(), all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
                new_calendar.sort_events_by_start_date()
                #6
                print("loading notion calendar")
                notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
                notion_calendar.sort_events_by_start_date()
                #8
                current_calendar.add_calendar(new_calendar=new_calendar)
                current_calendar.sort_events_by_start_date()
                #3
                print("uploading google calendar")
                calendar_save_to_google_drive(current_calendar)
                #30
                days_from_now = 0
                start_date = datetime_from_now(days_from_now)
                start_days_from_now = days_from_now
                #31
                days_from_now = 365
                end_date = datetime_from_now(days_from_now)
                end_days_from_now = days_from_now
                #20
                print("deleting notion calendar for next year")
                notion_calendar.notion_delete_calendar(start_days_from_now=start_days_from_now, end_days_from_now=end_days_from_now)
                notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
                notion_calendar.sort_events_by_start_date()
                #21
                print("uploading to notion calendar for next year")
                notion_update_pages(NOTION_DATABASE, new_calendar=current_calendar, start_days_from_now=start_days_from_now, end_days_from_now=end_days_from_now)
                #99
                break
            case 1:
                new_calendar = Calendar(google_events=get_all_google_events(), all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
                new_calendar.sort_events_by_start_date()
            case 2:
                new_calendar = Calendar(google_events=get_all_new_google_events(),all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
                new_calendar.sort_events_by_start_date()
            case 3:
                calendar_save_to_google_drive(current_calendar)
            case 4:
                current_calendar = calendar_load_from_google_drive()
                current_calendar.sort_events_by_start_date()
            case 5:
                print (f"start_date = {start_date}")
                print (f"end_date = {end_date}")
                print (f"new_calendar = {new_calendar}")
                print (f"current_calendar = {current_calendar}")
                print (f"notion_calendar = {notion_calendar}")
            case 6:
                notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
                notion_calendar.sort_events_by_start_date()
            case 7:
                notion_calendar.add_calendar(new_calendar=new_calendar)
                notion_calendar.sort_events_by_start_date()
            case 8:
                current_calendar.add_calendar(new_calendar=new_calendar)
                current_calendar.sort_events_by_start_date()
            case 9:
                current_calendar.add_calendar(new_calendar=notion_calendar)
                current_calendar.sort_events_by_start_date()
            case 10:
                new_calendar = Calendar()
            case 11:
                current_calendar = Calendar()
            case 12:
                notion_calendar = Calendar()
            case 20:
                if input(f"delete notion_calendar from {start_date} to {end_date}? (y/N)")=="y":
                    notion_calendar.notion_delete_calendar(start_days_from_now=start_days_from_now, end_days_from_now=end_days_from_now)
                    notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
                    notion_calendar.sort_events_by_start_date()
            case 21:
                if input(f"Upload current_calendar to Notion from {start_date} to {end_date}? (y/N)")=="y":
                    notion_update_pages(NOTION_DATABASE, new_calendar=current_calendar, start_days_from_now=start_days_from_now, end_days_from_now=end_days_from_now)
            case 30:
                if input(f"change start_date from {start_date}? (y/N) ") == "y":
                    try:
                        days_from_now = int(input ("days from now (pos integer number of days for future date, neg integer for past date  "))
                        start_date = datetime_from_now(days_from_now)
                        start_days_from_now = days_from_now
                        print (f"start_date = {start_date}")
                    except ValueError:
                        print ("needs to be an integer")
            case 31:
                if input(f"change end_date from {end_date}? (y/N) ") == "y":
                    try:
                        days_from_now = int(input ("days from now (pos integer number of days for future date, neg integer for past date  "))
                        end_date = datetime_from_now(days_from_now)
                        end_days_from_now = days_from_now
                        print (f"end_date = {end_date}")
                    except ValueError:
                        print ("needs to be an integer")
            case 77:
                #1
                print("loading google calendars")
                new_calendar = Calendar(google_events=get_all_google_events(), all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
                new_calendar.sort_events_by_start_date()
                #6
                print("loading notion calendar")
                notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
                notion_calendar.sort_events_by_start_date()
                #8
                # current_calendar.add_calendar(new_calendar=new_calendar)
                # current_calendar.sort_events_by_start_date()
                #3
                # print("uploading google calendar")
                # calendar_save_to_google_drive(current_calendar)
                #30
                days_from_now = 0
                start_date = datetime_from_now(days_from_now)
                start_days_from_now = days_from_now
                #31
                days_from_now = 365
                end_date = datetime_from_now(days_from_now)
                end_days_from_now = days_from_now
                #20
                print("deleting notion calendar for next year")
                notion_calendar.notion_delete_calendar(start_days_from_now=start_days_from_now, end_days_from_now=end_days_from_now)
                notion_calendar = Calendar(notion_database_id=NOTION_DATABASE, NOTION_API_KEY=NOTION_API_KEY)
                notion_calendar.sort_events_by_start_date()
                #21
                print("uploading to notion calendar for next year")
                notion_update_pages(NOTION_DATABASE, new_calendar=new_calendar, start_days_from_now=start_days_from_now, end_days_from_now=end_days_from_now)
                #99
                break
            case 99:
                break
            case _:
                print (f"{choice} is not a valid input")
            
