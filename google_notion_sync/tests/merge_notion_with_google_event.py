from copy import deepcopy
from datetime import date, datetime
import pickle

from pytz import timezone

from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.utils.configure import ALL_GOOGLE_CALENDARS_DICT
from google_notion_sync.utils.helpers import datetime_from_now, event_start_datetime


with open("./google_notion_sync/data/notion_calendar.pickle", "rb") as f:
    notion_calendar = pickle.load(f)

with open("./google_notion_sync/data/all_google_events.pickle", "rb") as f:
    all_google_events = pickle.load(f)

google_calendar = Calendar(google_events=all_google_events,all_google_calendars_dict=ALL_GOOGLE_CALENDARS_DICT)

print (notion_calendar)
print (google_calendar)
start_date = datetime_from_now(0)
end_date = datetime_from_now(30)
keep_events = [raw_event for raw_event in google_calendar.all_events if (event_start_datetime(raw_event)>=start_date and event_start_datetime(raw_event)<=end_date)]
keep_calendar = Calendar(events=keep_events)
keep_calendar.sort_events_by_start_date()
print (keep_calendar)
merged_calendar = deepcopy(notion_calendar)
merged_calendar.add_calendar(keep_calendar)
print (merged_calendar)
