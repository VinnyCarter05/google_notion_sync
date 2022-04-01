import os
import pickle

from google_notion_sync.classes.calendar import Calendar
from google_notion_sync.google_api.calendar import get_google_calendar_service, get_google_instances
from google_notion_sync.google_api.credentials import get_google_creds


with open ("./google_notion_sync/data/1.pickle","rb") as f:
    google_trial_events_1 = pickle.load(f)
with open ("./google_notion_sync/data/2.pickle","rb") as f:
    google_trial_events_2 = pickle.load(f)
with open ("./google_notion_sync/data/3.pickle","rb") as f:
    google_trial_events_3 = pickle.load(f)
with open ("./google_notion_sync/data/4.pickle","rb") as f:
    google_trial_events_4 = pickle.load(f)
with open ("./google_notion_sync/data/5.pickle","rb") as f:
    google_trial_events_5 = pickle.load(f)
with open ("./google_notion_sync/data/6.pickle","rb") as f:
    google_trial_events_6 = pickle.load(f)
with open ("./google_notion_sync/data/7.pickle","rb") as f:
    google_trial_events_7 = pickle.load(f)
with open ("./google_notion_sync/data/8.pickle","rb") as f:
    google_trial_events_8 = pickle.load(f)
with open ("./google_notion_sync/data/9.pickle","rb") as f:
    google_trial_events_9 = pickle.load(f)
with open ("./google_notion_sync/data/10.pickle","rb") as f:
    google_trial_events_10 = pickle.load(f)
with open ("./google_notion_sync/data/11.pickle","rb") as f:
    google_trial_events_11 = pickle.load(f)
with open ("./google_notion_sync/data/google_trial_events.pickle","rb") as f:
    google_trial_events = pickle.load(f)
combined_google_trial_events = google_trial_events_1+google_trial_events_2+google_trial_events_3 + google_trial_events_4 + google_trial_events_5+google_trial_events_6+google_trial_events_7+google_trial_events_8+google_trial_events_9

google_calendar = Calendar()
GOOGLE_DRIVE_FILE_ID = os.getenv('GOOGLE_DRIVE_FILE_ID')
SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/drive']
creds = get_google_creds(SCOPES, token_path='./google_notion_sync/config/token.json', credentials_path='./google_notion_sync/config/credentials.json')
calendar_service = get_google_calendar_service(creds)

print ("****************************")

for num, google_trial_event in enumerate(combined_google_trial_events):
    print (num, google_trial_event)
    try:
        print (num, "non-recurring: ", get_google_instances(calendar_service,google_trial_event['calendar'], google_trial_event['id']))
    except:
        print (num, "error non-recurring: ",google_trial_event)


