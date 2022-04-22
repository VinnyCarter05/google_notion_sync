import asyncio
from copy import copy, deepcopy
import pickle
from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.notion_api.database import async_notion_create_pages, async_notion_update_pages, notion_create_page

from google_notion_sync.utils.configure import ALL_GOOGLE_CALENDARS, HEADERS, NOTION_API_KEY, NOTION_DATABASE


def run ():
    notion_calendar = Calendar(notion_database_id=NOTION_DATABASE,  NOTION_API_KEY=NOTION_API_KEY)
    print (notion_calendar)
    with open("google_notion_sync/data/5changesingleevent.pickle", "rb") as f:
        google_trial_events_5 = pickle.load(f)
    new_calendar = Calendar(google_events=google_trial_events_5, all_google_calendars=ALL_GOOGLE_CALENDARS)
    print (new_calendar)
    merged_calendar = deepcopy(notion_calendar)
    merged_calendar.add_calendar(new_calendar=new_calendar)
    print (f"notion_calendar = {notion_calendar}\nmerged_calendar {merged_calendar}")
    # asyncio.run(async_notion_update_pages(NOTION_DATABASE, headers=HEADERS, events = [event for event in merged_calendar.all_events]))
    asyncio.run(async_notion_create_pages(NOTION_DATABASE=NOTION_DATABASE, headers=HEADERS, events=new_calendar.all_events))
    # notion_create_page(headers=HEADERS,payload = new_calendar.all_events[0].notion_payload)




if __name__ == "__main__":
    run()