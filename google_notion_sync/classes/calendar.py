# from dotenv import load_dotenv
# from decouple import config
import asyncio
import requests
import logging

import aiohttp

from google_notion_sync.classes.event import Event
from google_notion_sync.google_api.calendar import get_google_instances, google_calendar_sync_events_list
from google_notion_sync.notion_api.database import async_notion_delete_pages, async_notion_retrieve_page, notion_query_database, notion_retrieve_page
from google_notion_sync.utils.helpers import datetime_from_now, event_start_datetime
# import event
# import calendar_kit as ck

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)
import platform
if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Calendar:
    # def __init__ (self, notion_database_id="", googleCalendarId="", loadFrom = "notion",resync=True,timeMinDays=1,timeMaxDays=1):
    def __init__ (self, notion_database_id="", NOTION_API_KEY="", google_events=[], all_google_calendars=[], events = None):
    #(self, notion_database_id="", googleCalendarId="", NOTION_API_KEY = "", calendarService="", driveService="", googleDriveFileId="", loadFrom = "",resync=True,timeMinDays=1,timeMaxDays=1):
        self.NOTION_API_KEY = NOTION_API_KEY
        self.headers = {"Authorization": f"Bearer {self.NOTION_API_KEY}",
          "Content-Type": "application/json",
          "Notion-Version": "2022-02-22"}
        # self.service = calendarService
        self.notion_database_id = notion_database_id
        # self.googleCalendarId = googleCalendarId
        # self.driveService = driveService
        # self.googleDriveFileId = googleDriveFileId
        # self.resync=resync
        # self.timeMinDays=timeMinDays
        # self.timeMaxDays=timeMaxDays
        # self.date_min = datetime_from_now(-timeMinDays)
        # self.date_max = datetime_from_now(timeMaxDays)
        self.all_google_calendars = all_google_calendars
        self.all_events = []

        # if loadFrom == 'notion':
        if (notion_database_id != "" and NOTION_API_KEY != ""):
            self.load_from_notion()           
            return

        if google_events != []:
            logger.info(f"Calendar from google_events: {google_events}")
            self.from_google_calendar_events(google_events)
            # self.add_calendar_property(all_google_calendars=self.all_google_calendars)
            self.sort_events_by_start_date()
            return

        if events:
            self.all_events = events

        # if loadFrom == 'google':
        #     # rawEvents = self.queryGoogleEvents(googleCalendarId['id'],timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
        #     rawEvents = self.queryGoogleEvents(googleCalendarId['id'],driveService=self.driveService,googleDriveFileId=self.googleDriveFileId, timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
        #     # rawEvents = google_calendar_sync_events_list(self.service,self.driveService,google_drive_fileId=self.googleDriveFileId,calendar_id=self.googleCalendarId,resync=self.resync,timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
        #     # logger.info ('load from google rawEvents: ',rawEvents)
        #     self.googleRawEvents = rawEvents
        #     self.all_events, self.deleteEventList = self.getGoogleEventList(rawEvents,googleCalendarId,timeMinDays=self.timeMinDays,timeMaxDays=self.timeMaxDays)
        #     self.sort_events_by_google_id()
        #     return
        # else:
        #     self.all_notion_page_ids = []
        #     self.all_events = []

    def __repr__(self) -> str:
        all_events_list = f"Calendar with {len(self.all_events)} events: \n"
        for num, event in enumerate(self.all_events):
            if (num <= 10) or (num == len(self.all_events) - 1):
                all_events_list += f"{num}: {event}  \n"
        return all_events_list

    def __len__(self) -> int:
        return len (self.all_events)
        
    def load_from_notion(self):
        self.all_notion_page_ids = self.get_all_notion_event_ids(self.notion_database_id)
        logger.debug(f"all_notion_page_ids = {self.all_notion_page_ids}")
        if self.all_notion_page_ids:
            asyncio.run(self.get_notion_event_list(self.all_notion_page_ids))
            # self.all_events = self.get_notion_event_list (self.all_notion_page_ids)
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
            if r != None:
                if r.status_code >= 400:
                    logger.error (f"Status code to notion_database_query = {r.status_code}\n response headers = {r.headers}")
                    has_more = False
                else:
                    logger.info (f"r.json()['has_more'] = {r.json()['has_more']}, r.json()['next_cursor'] = {r.json()['next_cursor']}")
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
    
    async def get_notion_event_list (self, notionPageIdList):
        # notion_all_events = []
        # for pageId in notionPageIdList:
            # notion_all_events.append(self.get_notion_event(pageId))
        async with aiohttp.ClientSession() as session:
            notion_all_events = []
            for pageId in notionPageIdList:
                event = asyncio.ensure_future(self.get_notion_event(session, pageId))
                if event != None:
                    notion_all_events.append(event)
            self.all_events = await asyncio.gather(*notion_all_events)
        return #[self.get_notion_event(pageId) for pageId in notionPageIdList]
    
    async def get_notion_event (self, session, event_id):
        notion_event = await async_notion_retrieve_page(session,self.headers,event_id)
        """ url = f'https://api.notion.com/v1/pages/{event_id}'
        async with session.get(url, headers=self.headers) as response:
            try:
                notion_page = await response.json()
            except TypeError:
                return None

            print (f"notion_page = {notion_page}")
            notion_event = Event(notion_page=notion_page) """
        return notion_event

        """ r = notion_retrieve_page(session, self.headers, eventId)
        if r != None:
            if r.status_code >= 400:
                logger.error (f"get_notion_event status code = {r.status_code}")
                return None
            notion_event = Event(notion_page=r.json())
            # notion_event.from_notion_page(r.json())
            return notion_event
        else:
            return None """

    def delete_event(self, event=None, google_id=None, notion_id=None):#, del_all_instances = False):
        keep_events = []
        if google_id:
            for one_event in self.all_events:
                if not one_event.properites['googleId']==google_id:
                    keep_events.append(one_event)
        elif notion_id:
            for one_event in self.all_events:
                if not one_event.properties['notionId']==notion_id:
                    keep_events.append(one_event)
        elif event:
        #     if del_all_instances:
        #         for one_event in self.all_events:
        #             if not (event <= one_event):
        #                 keep_events.append(one_event)
        #     else:
            for one_event in self.all_events:
                if not(event == one_event):
                    keep_events.append(one_event)
        self.all_events = keep_events

        

    def add_calendar_property(self, all_google_calendars=[]):
        for count, event in enumerate(self.all_events):
            if event.properties['calendar']=="":
                try:
                    self.all_events[count].properties['calendar'] = [cal for cal in all_google_calendars if cal['id']==event['googleCalendar']][0]['summary']            
                except:
                    self.all_events[count] = ""

    def allProperties(self):
        propertyList = []
        for event in self.all_events:
            propertyList.append(event.properties) 
        return propertyList


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
                notion_event = Event(notion_page=r.json())
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

    def sort_events_by_start_date (self):
        self.all_events.sort(key=lambda x:x.properties['start'])
        return

    def matchedGoogleEvents(self, googleEventId):
        # returns list of events
        matchedEventList = []
        for matchedEvents in [x for x in self.allProperties() if ((x['googleId'] == googleEventId) or (x['recurringEventId'] == googleEventId))]:
            matchedEventList.append(matchedEvents)
        return matchedEventList
                                           
    def add_event(self, event):
        self.all_events.append(event)

    def from_google_calendar_events (self, google_calendar_events):
        for event in google_calendar_events:  # google_instances:
            ev = Event(google_event=event)
            self.all_events.append(ev)

    def any_canceled(self)-> bool:
        for event in self.all_events:
            if event.properties['googleStatus'] == 'cancelled':
                return True
        return False

    def add_calendar(self, new_calendar):
        # adds Calendar class new_calendar -- all_events to self
        logger.info(f"self.all_events = {self.all_events}")
        # current_calendar = Calendar(google_events=self.all_events,all_google_calendars=self.all_google_calendars) 
        current_calendar = Calendar(events = self.all_events)
        current_calendar.sort_events_by_google_id()
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
                if new_event.properties['googleStatus'] != 'cancelled':
                    keep_calendar.add_event(new_event)
                new_counter += 1
                continue
            if new_end:
                if cur_event.properties['googleStatus'] != 'cancelled':
                    keep_calendar.add_event(cur_event)
                cur_counter += 1
                continue
            if cur_event <= new_event:
                if new_event.properties['googleStatus'] != 'cancelled':
                    keep_calendar.add_event(new_event)
                cur_counter += 1
                new_counter += 1
                continue
            if cur_event < new_event:
                if cur_event.properties['googleStatus'] != 'cancelled':
                    keep_calendar.add_event(cur_event)
                cur_counter += 1
            else:
                if new_event.properties['googleStatus'] != 'cancelled':
                    keep_calendar.add_event(new_event)
                new_counter += 1
        keep_calendar.sort_events_by_google_id()
        self.all_events = keep_calendar.all_events

    def notion_delete_calendar (self, days_from_now = 36500):
        del_events_notion_page_ids = []
        for event in self.all_events:
            event_start_dt = event_start_datetime(event=event)
            after_dt = datetime_from_now(days_from_now)
            print (f"{event} {event_start_dt} {after_dt}")
            if event_start_dt > after_dt:
                del_events_notion_page_ids.append(event.properties['notionId'])
        print (f"del_events_notion_page_ids = {del_events_notion_page_ids}")

        asyncio.run(async_notion_delete_pages(headers=self.headers, notion_page_ids=del_events_notion_page_ids))
        for notion_id in del_events_notion_page_ids:
            self.delete_event(notion_id=notion_id)