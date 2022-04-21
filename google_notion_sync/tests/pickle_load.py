import logging
import os
import pickle
from types import new_class

from dotenv import load_dotenv
from google_notion_sync.classes.calendar import Calendar

from google_notion_sync.classes.event import Event
from google_notion_sync.google_api.calendar import get_all_google_calendars, get_google_calendar_service
from google_notion_sync.google_api.credentials import get_google_creds
from google_notion_sync.google_api.drive import get_google_drive_service, google_drive_download_file, google_drive_file_upload
from google_notion_sync.utils.configure import CALENDAR_SERVICE
from google_notion_sync.utils.helpers import pickle_load

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                    filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

# SCOPES = ['https://www.googleapis.com/auth/calendar',
#           'https://www.googleapis.com/auth/drive']
# creds = get_google_creds(SCOPES, token_path='./google_notion_sync/config/token.json',
#                          credentials_path='./google_notion_sync/config/credentials.json')
# calendar_service = get_google_calendar_service(creds)
# drive_service = get_google_drive_service(creds)
all_google_calendars = get_all_google_calendars(CALENDAR_SERVICE)


with open("./google_notion_sync/data/notion_calendar.pickle", "rb") as f:
    notion_calendar = pickle.load(f)

with open("./google_notion_sync/data/all_google_events.pickle", "rb") as f:
    all_google_events = pickle.load(f)

""" print(len(notion_calendar.all_events))
print(len(all_google_events))
 """
with open("google_notion_sync/data/1resync.pickle", "rb") as f:
    google_trial_events_1 = pickle.load(f)
with open("google_notion_sync/data/2noresync.pickle", "rb") as f:
    google_trial_events_2 = pickle.load(f)
with open("google_notion_sync/data/3del_single_event.pickle", "rb") as f:
    google_trial_events_3 = pickle.load(f)
with open("google_notion_sync/data/4changefollingevents.pickle", "rb") as f:
    google_trial_events_4 = pickle.load(f)
with open("google_notion_sync/data/5changesingleevent.pickle", "rb") as f:
    google_trial_events_5 = pickle.load(f)
with open("google_notion_sync/data/6delallofoneeent.pickle", "rb") as f:
    google_trial_events_6 = pickle.load(f)
with open("google_notion_sync/data/7del_all_events.pickle", "rb") as f:
    google_trial_events_7 = pickle.load(f)
with open("google_notion_sync/data/8create_repeating_event.pickle", "rb") as f:
    google_trial_events_8 = pickle.load(f)
with open("google_notion_sync/data/9create_single_event.pickle", "rb") as f:
    google_trial_events_9 = pickle.load(f)
with open("google_notion_sync/data/10change_single_to_repeat.pickle", "rb") as f:
    google_trial_events_10 = pickle.load(f)
with open("google_notion_sync/data/11add_event_j.pickle", "rb") as f:
    google_trial_events_11 = pickle.load(f)
with open("google_notion_sync/data/12change_to_repeat_j.pickle", "rb") as f:
    google_trial_events_12 = pickle.load(f)
with open("google_notion_sync/data/13lots_of_changes.pickle", "rb") as f:
    google_trial_events_13 = pickle.load(f)
# with open("./google_notion_sync/data/google_trial_events.pickle", "rb") as f:
#     google_trial_events = pickle.load(f)

# print('1:', google_trial_events_1)
# print("2:", google_trial_events_2)
# print("3:", google_trial_events_3)
# print("4:", google_trial_events_4)
# print("5:", google_trial_events_5)
# print("6:", google_trial_events_6)
# print("7:", google_trial_events_7)
# print("8:", google_trial_events_8)
# print("9:", google_trial_events_9)
# print ("10:", google_trial_events_10)
print ("13:", google_trial_events_13)
# print ("google_trial_events:", google_trial_events)

combined_google_trial_events = google_trial_events_1+google_trial_events_2+google_trial_events_3 + google_trial_events_4 + \
    google_trial_events_5+google_trial_events_6+google_trial_events_7 + \
    google_trial_events_8+google_trial_events_9

current_calendar = Calendar(
    google_events=google_trial_events_1, all_google_calendars=all_google_calendars)
current_calendar.sort_events_by_google_id()
# print(current_calendar)
new_calendar = Calendar(google_events=google_trial_events_3,
                        all_google_calendars=all_google_calendars)
new_calendar.sort_events_by_google_id()
# print(new_calendar)

keep_calendar = Calendar()
keep_events = []
cur_counter = 0
new_counter = 0
cur_end = False
new_end = False
while True:
    if cur_counter < len(current_calendar.all_events):
        cur_event = current_calendar.all_events[cur_counter]
        # print("cur_event= ",
        #       cur_event.properties['googleId'], cur_event.properties['googleStatus'])
    else:
        cur_end = True
    if new_counter < len(new_calendar.all_events):
        new_event = new_calendar.all_events[new_counter]
        # print("new_event= ",
        #       new_event.properties['googleId'], new_event.properties['googleStatus'])
    else:
        new_end = True
    if cur_end and new_end:
        break
    if cur_end:
        if new_event.properties['googleStatus'] == 'confirmed':
            keep_events.append(new_event)
            keep_calendar.add_event(new_event)
        new_counter += 1
        continue
    if new_end:
        if cur_event.properties['googleStatus'] == 'confirmed':
            keep_events.append(cur_event)
            keep_calendar.add_event(cur_event)
        cur_counter += 1
        continue
    if cur_event <= new_event or cur_event == new_event:
        if new_event.properties['googleStatus'] == 'confirmed':
            keep_events.append(new_event)
            keep_calendar.add_event(new_event)
        cur_counter += 1
        new_counter += 1
        continue
    if cur_event < new_event:
        if cur_event.properties['googleStatus'] == 'confirmed':
            keep_events.append(cur_event)
            keep_calendar.add_event(cur_event)
        cur_counter += 1
    else:
        if new_event.properties['googleStatus'] == 'confirmed':
            keep_events.append(new_event)
            keep_calendar.add_event(new_event)
        new_counter += 1

# print(keep_events,'\n\n')
# print(list(filter(lambda event:cur_event.properties['googleId']==event.properties['googleId'],new_calendar.all_events)))

# match = [ev for ev in current_calendar.all_events if ev.properties['googleId']
#          == event.properties['googleId']]
# matches.extend(match)
all_event_list = [google_trial_events_1, google_trial_events_2, google_trial_events_3, google_trial_events_4, google_trial_events_5, google_trial_events_6,
                  google_trial_events_7, google_trial_events_8, google_trial_events_9, google_trial_events_10,
                  google_trial_events_11, google_trial_events_12, google_trial_events_13]
keep_calendar = Calendar()
for events in all_event_list:
    new_calendar = Calendar(google_events=events, all_google_calendars=all_google_calendars)
    keep_calendar.add_calendar(new_calendar=new_calendar)
    """ current_calendar = keep_calendar
    current_calendar.sort_events_by_google_id()
    new_calendar = Calendar(google_events=events,
                            all_google_calendars=all_google_calendars)
    new_calendar.sort_events_by_google_id()
    logger.info(f"current_calendar = {current_calendar}\n")
    logger.info(f"new_calendar = {new_calendar}\n\n")
    keep_calendar = Calendar()
    cur_counter = 0
    new_counter = 0
    cur_end = False
    new_end = False
    while True:
        if cur_counter < len(current_calendar.all_events):
            cur_event = current_calendar.all_events[cur_counter]
        else:
            cur_end = True
        if new_counter < len(new_calendar.all_events):
            new_event = new_calendar.all_events[new_counter]
        else:
            new_end = True
        if cur_end and new_end:
            break
        if cur_end:
            if new_event.properties['googleStatus'] == 'confirmed':
                keep_calendar.add_event(new_event)
            new_counter += 1
            continue
        if new_end:
            if cur_event.properties['googleStatus'] == 'confirmed':
                keep_calendar.add_event(cur_event)
            cur_counter += 1
            continue
        if cur_event <= new_event:
            if new_event.properties['googleStatus'] == 'confirmed':
                keep_calendar.add_event(new_event)
            cur_counter += 1
            new_counter += 1
            continue
        if cur_event < new_event:
            if cur_event.properties['googleStatus'] == 'confirmed':
                keep_calendar.add_event(cur_event)
            cur_counter += 1
        else:
            if new_event.properties['googleStatus'] == 'confirmed':
                keep_calendar.add_event(new_event)
            new_counter += 1"""
for event in keep_calendar.all_events:
    print (event,"\n")
 