import logging
import pickle

from google_notion_sync.classes.event import Event

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

with open ("./google_notion_sync/data/notion_calendar.pickle","rb") as f:
    notion_calendar = pickle.load(f)

with open ("./google_notion_sync/data/all_google_events.pickle","rb") as f:
    all_google_events = pickle.load(f)

print (len(notion_calendar.all_events))
print (len(all_google_events))

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

print ('1:', google_trial_events_1)
print ("2:", google_trial_events_2)
print ("3:", google_trial_events_3)
print ("4:", google_trial_events_4)
print ("5:", google_trial_events_5)
print ("6:", google_trial_events_6)
print ("7:", google_trial_events_7)
print ("8:", google_trial_events_8)
print ("9:", google_trial_events_9)
print ("10:", google_trial_events_10)
print ("11:", google_trial_events_11)
# print ("google_trial_events:", google_trial_events)

combined_google_trial_events = google_trial_events_1+google_trial_events_2+google_trial_events_3 + google_trial_events_4 + google_trial_events_5+google_trial_events_6+google_trial_events_7+google_trial_events_8+google_trial_events_9

# print (all_google_events)
# for event in combined_google_trial_events:
#     print (event['status'], event['id'], event.keys())

# for i in range(5):
#     print (f"\nall_google_events {i}:", all_google_events[i])