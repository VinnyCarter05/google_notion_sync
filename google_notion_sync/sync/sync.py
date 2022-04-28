import asyncio
from calendar import Calendar
from copy import deepcopy
import logging

from google_notion_sync.notion_api.database import async_notion_update_pages

from google_notion_sync.utils.configure import ALL_GOOGLE_CALENDARS_DICT, HEADERS, NOTION_API_KEY, NOTION_DATABASE

logger = logging.getLogger(__name__)

def update_notion_database (new_google_events):
    notion_calendar = Calendar(notion_database_id=NOTION_DATABASE,  NOTION_API_KEY=NOTION_API_KEY)
    logger.info (f"updating notion_calendar = {notion_calendar}")
    new_calendar = Calendar(google_events=new_google_events, all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)
    logger.info (f"adding new_calendar = {new_calendar}")
    merged_calendar = deepcopy(notion_calendar)
    merged_calendar.add_calendar(new_calendar=new_calendar)
    asyncio.run(async_notion_update_pages(NOTION_DATABASE, headers=HEADERS, events = [event for event in merged_calendar.all_events]))
