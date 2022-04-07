# from dotenv import load_dotenv
# from decouple import config
import requests
import logging

from google_notion_sync.classes.event import Event
from google_notion_sync.google_api.calendar import get_google_instances, google_calendar_sync_events_list
from google_notion_sync.notion_api.database import notion_query_database, notion_retrieve_page
from google_notion_sync.utils.helpers import datetime_from_now
# import event
# import calendar_kit as ck

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

class Calendar:
    # def __init__ (self, notion_database_id="", googleCalendarId="", loadFrom = "notion",resync=True,timeMinDays=1,timeMaxDays=1):
    def __init__ (self, notion_database_id="", googleCalendarId="", NOTION_API_KEY = "", calendarService="", driveService="", googleDriveFileId="", loadFrom = "",resync=True,timeMinDays=1,timeMaxDays=1):
        self.NOTION_API_KEY = NOTION_API_KEY
        self.headers = {"Authorization": f"Bearer {self.NOTION_API_KEY}",
          "Content-Type": "application/json",
          "Notion-Version": "2022-02-22"}
        self.service = calendarService
        self.notion_database_id = notion_database_id
        self.googleCalendarId = googleCalendarId
        self.driveService = driveService
        self.googleDriveFileId = googleDriveFileId
        self.resync=resync
        self.timeMinDays=timeMinDays
        self.timeMaxDays=timeMaxDays
        self.date_min = datetime_from_now(-timeMinDays)
        self.date_max = datetime_from_now(timeMaxDays)
        self.all_events = []

        if loadFrom == 'notion':
            self.load_from_notion()           
            return

        if loadFrom == 'google':
            # rawEvents = self.queryGoogleEvents(googleCalendarId['id'],timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
            rawEvents = self.queryGoogleEvents(googleCalendarId['id'],driveService=self.driveService,googleDriveFileId=self.googleDriveFileId, timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
            # rawEvents = google_calendar_sync_events_list(self.service,self.driveService,google_drive_fileId=self.googleDriveFileId,calendar_id=self.googleCalendarId,resync=self.resync,timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
            # logger.info ('load from google rawEvents: ',rawEvents)
            self.googleRawEvents = rawEvents
            self.all_events, self.deleteEventList = self.getGoogleEventList(rawEvents,googleCalendarId,timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
            self.sort_events_by_google_id()
            return
        else:
            self.all_notion_page_ids = []
            self.all_events = []

    def __repr__(self) -> str:
        all_events_list = f"Calendar with {len(self.all_events)} events: \n"
        for num, event in enumerate(self.all_events):
            if (num <= 10) or (num == len(self.all_events) - 1):
                all_events_list += f"{num}: {event}  \n"
        return all_events_list

    def __len__(self) -> int:
        return len (self.all_events)
        
    def allProperties(self):
        propertyList = []
        for event in self.all_events:
            propertyList.append(event.properties) 
        return propertyList

    def load_from_notion(self):
        self.all_notion_page_ids = self.get_all_notion_event_ids(self.notion_database_id)
        logger.warning(f"all_notion_page_ids = {self.all_notion_page_ids}")
        self.all_events = self.get_notion_event_list (self.all_notion_page_ids)
        self.sort_events_by_google_id()
        return 

    def get_all_notion_event_ids (self, databaseId):
        notion_all_page_ids = []
        next_cursor = None
        has_more = True
        payload = {"page_size": 100}
        while has_more:
            logger.info (f"payload = {payload}")
            r = notion_query_database(databaseId, headers=self.headers, payload=payload)
            logger.info (f"r.json()['has_more'] = {r.json()['has_more']}, r.json()['next_cursor'] = {r.json()['next_cursor']}")
            if r != None:
                results = r.json()['results']
                has_more = r.json()['has_more']
                next_cursor = r.json()['next_cursor']
                payload["start_cursor"]=next_cursor
                for i in range(len(results)):
                    notion_all_page_ids.append(results[i]['id']) 
            else:
                has_more = False
        if notion_all_page_ids == []:
            notion_all_page_ids = None
        return notion_all_page_ids
    
    def get_notion_event_list (self, notionPageIdList):
        notion_all_events = []
        for pageId in notionPageIdList:
            notion_all_events.append(self.get_notion_event(pageId))
        return notion_all_events
    
    def get_notion_event (self, eventId):
        r = notion_retrieve_page(self.headers,eventId)
        if r != None:
            notion_event = Event(notion_page=r.json())
            # notion_event.from_notion_page(r.json())
            return notion_event
        else:
            return None

    def delete_event(self, event, del_all_instances = False):
        keep_events = []
        if del_all_instances:
            for one_event in self.all_events:
                if not (event <= one_event):
                    keep_events.append(one_event)
        else:
            for one_event in self.all_events:
                if not(event == one_event):
                    keep_events.append(one_event)
        self.all_events = keep_events    
            

    def getNotionEventFromGoogleId(self, databaseId, googleId):
        url = f'https://api.notion.com/v1/databases/{databaseId}/query'
        payload = {
            "filter":{
                "property": "googleId",
                "rich_text":{
                    "contains": googleId
                    }
            }
        }
        try:
            r = requests.post(url,headers=self.headers,json=payload)
            if r.json != {}:
                notion_event = Event()
                notion_event.from_notion_page(r.json())
            else:
                notion_event = None
        except:
            logger.error ('Error retrieving Notion Event from GoogleId')
            notion_event = None
        return notion_event

    
    def postNotionEvent (self, postEvent, notion_database_id=""):
        if notion_database_id == "":
            notion_database_id = self.notion_database_id
        return postEvent.toNotionPage(notion_database_id,self.NOTION_API_KEY)
    
    def deleteNotionEvent (self, deleteEvent):
        return deleteEvent.deleteNotionPage()
    
    def updateNotionEvent (self, updateEvent):
        return updateEvent.updateNotionPage(self.notion_database_id)
                
    def sortEventsByNotionleId (self):
        self.all_events.sort(key=lambda x:x.properties['notionId'])
        return
 
    def postNotionall_events (self, notion_database_id=""):
        if notion_database_id=="":
            notion_database_id = self.notion_database_id
        for postEvent in self.all_events:
            postEvent.toNotionPage(notion_database_id,self.NOTION_API_KEY)
        for deleteEvent in self.deleteEventList:
            for property in self.allProperties:
                if deleteEvent.properties['googleId'] == property['googleId']:
                    deleteEvent.properties['notionId'] = property['notionId']
            if deleteEvent.properties['notionId']!="":
                deleteEvent.deleteNotionPage()
            
    def deleteNotionall_events (self, notion_database_id=""):
        if notion_database_id=="":
            notion_database_id = self.notion_database_id
        for postEvent in self.all_events:
            postEvent.deleteNotionPage()

    # def queryGoogleEvents (self, googleCalendarId,timeMinDays=1,timeMaxDays=1):
    def queryGoogleEvents (self, googleCalendarId,driveService,googleDriveFileId="",timeMinDays=1,timeMaxDays=1):
        # all_events = ck.syncEvents(self.service,calendarId=googleCalendarId,resync=self.resync,timeMinDays=timeMinDays,timeMaxDays=timeMaxDays)
        all_events = google_calendar_sync_events_list(self.service,driveService,google_drive_fileId=googleDriveFileId,calendar_id=googleCalendarId,resync=self.resync,timeMinDays=timeMinDays,timeMaxDays=timeMaxDays)
        return all_events
    
    def getGoogleEventList (self, rawEvents, googleCalendarId,timeMinDays=1,timeMaxDays=1):
        allGoogleEvents = []
        deleteGoogleEventList = []
        for rawEvent in rawEvents:
            newGoogleEvent = Event()
            newGoogleEvent.fromGoogleEvent(rawEvent, googleCalendarId['summary'])
            if newGoogleEvent.properties['googleStatus'] == 'cancelled':
                # logger.info("found a cancelled event",newGoogleEvent.properties)
                deleteGoogleEventList.append(newGoogleEvent)
                continue
            if newGoogleEvent.properties['start']!="": # do not append if no start time               
                if (newGoogleEvent.properties['recurrence']!=""):
                    allInstances = newGoogleEvent.getGoogleInstances (self.service, googleCalendarId,timeMinDays=timeMinDays,timeMaxDays=timeMaxDays)
                    for rawInstance in allInstances:
                        newGoogleInstance = Event()
                        newGoogleInstance.fromGoogleEvent(rawInstance, googleCalendarId['summary'])
                        allGoogleEvents.append(newGoogleInstance)
                        # logger.info ("instance: ", rawInstance,"from event:", rawEvent)
                else:
                    allGoogleEvents.append(newGoogleEvent)
                    # logger.info ("event: ", rawEvent)
            # else:
                # logger.info('no start time:',newGoogleEvent.properties)
        return allGoogleEvents, deleteGoogleEventList
    
    def getGoogleInstances (self, googleCalendarId, googleEventId,timeMinDays=1,timeMaxDays=1):
        return get_google_instances (self.service, calendarId=googleCalendarId, eventId=googleEventId,timeMinDays=timeMinDays,timeMaxDays=timeMaxDays)

    def sort_events_by_google_id (self):
        self.all_events.sort(key=lambda x:x.properties['googleId'])
        return

    def matchedGoogleEvents(self, googleEventId):
        # returns list of events
        matchedEventList = []
        for matchedEvents in [x for x in self.allProperties() if ((x['googleId'] == googleEventId) or (x['recurringEventId'] == googleEventId))]:
            matchedEventList.append(matchedEvents)
        return matchedEventList
                                           
    def addEvent(self, event):
        self.all_events.append(event)

    def from_google_calendar_events (self, google_calendar_events):
        for event in google_calendar_events:  # google_instances:
            ev = Event(google_event=event)
            self.all_events.append(ev)