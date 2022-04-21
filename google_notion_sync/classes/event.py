# import requests
# from dotenv import load_dotenv
# from decouple import config
import datetime
# import calendar_kit as ck
import pytz
import logging

import requests

from google_notion_sync.google_api.calendar import get_google_instances

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

class Event:
    def __init__ (self, google_event = None, notion_page = None):#, googleId="", googleCreated="", googleUpdated="", googleStatus="",
                #   notionId="", notionCreated="", notionUpdated="", 
                #   summary="", calendar="", description="", location="", 
                #   start="", end="", allDay=False, timeZone="", recurrence="",NOTION_API_KEY="", all_google_calendars=[]):
        self.properties = {'googleId':"",#googleId,
                           'googleCreated':"",#googleCreated,
                           'googleUpdated':"",#googleUpdated,
                           'googleStatus':"",#googleStatus,
                           'googleCalendar':"",
                           'notionId':"",#notionId,
                           'notionCreated':"",#notionCreated,
                           'notionUpdated':"",#notionUpdated,
                           'summary':"",#summary,
                           'calendar':"",#calendar,
                           'description':"",#description,
                           'location':"",#location,
                           'start':"",#start,
                           'end':"",#end,
                           'allDay':"",#allDay,
                           'timeZone':"",#timeZone,
                           'recurrence':""#recurrence
                          }
        # self.all_google_calendars = all_google_calendars
        # load_dotenv() 
        # self.NOTION_API_KEY = NOTION_API_KEY
        # self.headers = {"Authorization": f"Bearer {self.NOTION_API_KEY}",
        #                 "Content-Type": "application/json",
        #                 "Notion-Version": "2021-08-16"}
        if google_event != None: # if google_event is provided, initialize values
            self.from_google_event(google_event)
        if notion_page != None:
            self.from_notion_page(notion_page)

    def __repr__(self) -> str:
        return f"Event (googleId: {self.properties['googleId']}  summary: {self.properties['summary']}  status: {self.properties['googleStatus']} start: {self.properties['start']} calendar: {self.properties['calendar']} gooCal: {self.properties['googleCalendar']})"

    def __eq__(self, __o: object) -> bool:
        return self.properties['googleId']== __o.properties['googleId']

    def __ne__(self, __o: object) -> bool:
        if __o == None:
            return True
        return self.properties['googleId'][:26]!= __o.properties['googleId'][:26]

    def __gt__(self, __o: object) -> bool:
        # returns true if self is an instance of __o
        return self.properties['googleId']>__o.properties['googleId']

    def __ge__(self, __o: object) -> bool:
        # returns true if self is an instance of __o or is the same googleId
        return (self.properties['googleId'][:26]== __o.properties['googleId'][:26] and len(self.properties['googleId'])>=len(__o.properties['googleId'])) 

    def __lt__(self, __o: object) -> bool:
        # returns true if __o is an instance of self
        return self.properties['googleId']< __o.properties['googleId']

    def __le__(self, __o: object) -> bool:
        # returns true if __o is an instance of self
        return (self.properties['googleId'][:26]== __o.properties['googleId'][:26] and len(self.properties['googleId'])<=len(__o.properties['googleId']))


    def from_google_event(self, google_event):
                #, googleCalendar=None):
        try:
            self.properties['googleCalendar']=google_event['calendar']
            # if self.all_google_calendars != []:
                # self.properties['calendar'] = [i for i in self.all_google_calendars if i['id']==google_event['calendar']][0]['summary']
            # else:
                # self.properties['calendar'] = ""
        except:
            self.properties['googleCalendar'] = ""
            # self.properties['calendar'] = ""
            logger.warning(f"google_event no 'googleCalendar'")
        try:
            self.properties['googleId'] = google_event['id']
        except:
            self.properties['googleId'] = ""
            logger.warning(f"google_event no 'id'")
        try:
            self.properties['googleCreated'] = google_event['created']
        except:
            self.properties['googleCreated'] = ""
            logger.warning(f"google_event no 'created'")
        try:
            self.properties['googleUpdated'] = google_event['updated']
        except:
            self.properties['googleUpdated'] = ""
            logger.warning(f"google_event no 'updated'")
        try:
            self.properties['googleStatus'] = google_event['status']
        except:
            self.properties['googleStatus'] = ""
            logger.warning(f"google_event no 'status'")
        try:
            self.properties['summary'] = google_event['summary']
        except:
            self.properties['summary'] = ""
            logger.warning(f"google_event no 'summary'")
        try:
            self.properties['description'] = google_event['description']
        except:
            self.properties['description'] = ""
            logger.warning(f"google_event no 'description'")
        try:
            self.properties['location'] = google_event['location']
        except:
            self.properties['location'] = ""
            logger.warning(f"google_event no 'location'")
        try:
            self.properties['recurrence'] = google_event['recurrence']
        except:
            self.properties['recurrence'] = ""
            logger.warning(f"google_event no 'recurrence'")
        try:
            self.properties['start'] = google_event['start']['dateTime']
            self.properties['allDay'] = False
        except:
            try:
                self.properties['start'] = google_event['start']['date']
                self.properties['allDay'] = True
                logger.warning(f"google_event no 'start date'")
            except:
                self.properties['start'] = ""
        try:
            self.properties['end'] = google_event['end']['dateTime']
        except:
            try:
                self.properties['end'] = google_event['end']['date']
                # if all day event, need to subtract one day from end
                utc=pytz.UTC
                endAsDt = datetime.datetime.fromisoformat((self.properties['end']).rstrip('Z')).replace(tzinfo=utc)
                newEndAsDt = endAsDt - datetime.timedelta(days=1)
                self.properties['end'] = newEndAsDt.date().isoformat()
                logger.warning(f"google_event no 'end date'")
                # logger.info ('changed end date to:',self.properties['end'])
            except:
                self.properties['end'] = ""
        try:
            self.properties['timeZone'] = google_event['start']['timeZone']
        except:
            self.properties['timeZone'] = ""
            logger.warning(f"google_event no 'timeZone'")
        try:
            self.properties['recurringEventId'] = google_event['recurringEventId']
        except:
            self.properties['recurringEventId'] = ""
            logger.warning(f"google_event no 'recurringEventId'")

        # logger.info(google_event)
        # if self.properties['start'] == "":
            # logger.info ('start ==""', google_event)
            # try:
            #     self.properties['start'] = google_event['originalStartDate']['dateTime']
            #     self.properties['end'] = google_event['end']['dateTime']
            #     self.properties['timeZone'] = google_event['originalStartDate']['timeZone']
            #     self.properties['allDay'] = False
            # except:
            #     try:
            #         self.properties['start'] = google_event['originalStartDate']['date']
            #         self.properties['allDay'] = True
            #     except:
            #         self.properties['start'] = ""
            #         self.properties['end'] = ""
                    # self.properties['allDay'] = False
            
                
    def from_notion_page(self, notion_page):# fromnotion_page(self, notion_page):
        self.properties['notionId'] = notion_page['id']
        self.properties['notionCreated'] = notion_page['created_time']
        self.properties['notionUpdated'] = notion_page['last_edited_time']
        try:
            self.properties['googleId'] = notion_page['properties']['googleId']['rich_text'][0]['text']['content']
        except:
            self.properties['googleId'] = ""
        try:
            self.properties['googleCreated'] = notion_page['properties']['googleCreated']['rich_text'][0]['text']['content']
        except:
            self.properties['googleCreated'] = ""
        try:
            self.properties['googleUpdated'] = notion_page['properties']['googleUpdated']['rich_text'][0]['text']['content']
        except:
            self.properties['googleUpdated'] = ""
        try:
            self.properties['summary'] = notion_page['properties']['Summary']['title'][0]['text']['content']
        except:
            self.properties['summary'] = ""
        try:
            self.properties['calendar'] = notion_page['properties']['Calendar']['multi_select'][0]['name']
        except:
            self.properties['calendar'] = ""
        try:
            self.properties['googleCalendar'] = notion_page['properties']['googleCalendar']['rich_text'][0]['text']['content']
        except:
            self.properties['googleCalendar'] = ""
        try:
            self.properties['description'] = notion_page['properties']['Description']['rich_text'][0]['text']['content']
        except:
            self.properties['description'] = ""
        try:
            self.properties['location'] = notion_page['properties']['Location']['rich_text'][0]['text']['content']
        except:
            self.properties['location'] = ""
        self.properties['allDay'] = False
        try:
            self.properties['start'] = notion_page['properties']['Date']['date']['start']
            if "T" not in self.properties['start']:
                self.properties['allDay'] = True
        except:
            self.properties['start'] = ""
        try:
            self.properties['end'] = notion_page['properties']['Date']['date']['end']
        except:
            self.properties['end'] = ""
        try:
            self.properties['timeZone'] = notion_page['properties']['Date']['date']['time_zone']
        except:
            self.properties['timeZone'] = ""    
        try:
            self.properties['recurrence'] = notion_page['properties']['recurrence']['rich_text'][0]['text']['content']
        except:
            self.properties['recurrence'] = ""
        if self.properties['start']=="":
            self.properties['start']=datetime.date.today().isoformat()
        if self.properties['end']=="":
            self.properties['end']=None#self.properties['start']
        try:
            self.properties['recurringEventId'] = notion_page['properties']['recurringEventId']['rich_text'][0]['text']['content']
        except:
            self.properties['recurringEventId'] = ""
    

    def notion_payload (self, NOTION_DATABASE):
        endDate = self.properties['end']
        if endDate == self.properties['start']:
            endDate = None
        payload = {
        'parent': {'database_id': NOTION_DATABASE},
        'properties': {'Calendar': 
                        {'multi_select': 
                        [
                            {'name': self.properties['calendar'].replace(',','')[:99]}
                        ]
                        },
                        'googleCalendar': 
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['googleCalendar'][:199]}
                            }
                        ]
                        },
                        'Description': 
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['description'][:199]}
                            }
                        ]
                        },
                        'Date': 
                        {'date': 
                        {'start':self.properties['start'],
                            'end':endDate
                        }
                        },
                        'recurrence': 
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':str(self.properties['recurrence'])}
                            }
                        ]
                        },
                        'Location': 
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['location']}
                            }
                        ]
                        },
                        'Summary': 
                        {'title': 
                        [
                            {'text': 
                                {'content':self.properties['summary']}
                            }
                        ]
                        },
                        'googleId':
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['googleId']}
                            }
                        ]
                        },
                        'googleCreated':
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['googleCreated']}
                            }
                        ]
                        },
                        'googleUpdated':
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['googleUpdated']}
                            }
                        ]
                        },
                        'recurringEventId':
                        {'rich_text': 
                        [
                            {'text': 
                                {'content':self.properties['recurringEventId']}
                            }
                        ]
                        }
                        }
        }
        return payload

"""
    def add_notion_page(self, NOTION_DATABASE, headers):
        endDate = self.properties['end']
        if endDate == self.properties['start']:
            endDate = None
        payload = {
            'parent': {'database_id': NOTION_DATABASE},
            'properties': {'Calendar': 
                           {'multi_select': 
                            [
                                {'name': self.properties['calendar'].replace(',','')[:99]}
                            ]
                           },
                            'googleCalendar': 
                            {'rich_text': 
                            [
                                {'text': 
                                    {'content':self.properties['googleCalendar'][:199]}
                                }
                            ]
                            },
                           'Description': 
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['description'][:199]}
                                }
                            ]
                           },
                           'Date': 
                           {'date': 
                            {'start':self.properties['start'],
                             'end':endDate
                            }
                           },
                           'recurrence': 
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':str(self.properties['recurrence'])}
                                }
                            ]
                           },
                           'Location': 
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['location']}
                                }
                            ]
                           },
                           'Summary': 
                           {'title': 
                            [
                                {'text': 
                                 {'content':self.properties['summary']}
                                }
                            ]
                           },
                           'googleId':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['googleId']}
                                }
                            ]
                           },
                           'googleCreated':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['googleCreated']}
                                }
                            ]
                           },
                           'googleUpdated':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['googleUpdated']}
                                }
                            ]
                           },
                           'recurringEventId':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['recurringEventId']}
                                }
                            ]
                           }
                          }
        }
        # from google_notion_sync.notion_api.database import notion_create_page

        # r = notion_create_page(headers=headers, payload=payload)
        url = 'https://api.notion.com/v1/pages'
        # logger.info (payload)
        r = requests.post(url, headers=headers, json=payload)
        # logger.info(r.json())
        self.properties['notionId'] = r.json()['id']
        self.properties['notionCreated'] = r.json()['created_time']
        self.properties['notionUpdated'] = r.json()['last_edited_time']
        return r
        
    def updateNotionPage(self, NOTION_DATABASE):
        if self.properties['notionId'] == "":
            logger.warning ("page doesn't exist.  Creating page instead of updating")
            return self.toNotionPage(NOTION_DATABASE)
        payload = {
            'properties': {'Calendar': 
                           {'multi_select': 
                            [
                                {'name': self.properties['calendar'].replace(',','')[:99]}
                            ]
                           },
                           'Description': 
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['description'][:1999]}
                                }
                            ]
                           },
                           'Date': 
                           {'date': 
                            {'start':self.properties['start'],
                             'end':self.properties['end']}
                           },
                           'recurrence': 
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':str(self.properties['recurrence'])}
                                }
                            ]
                           },
                           'Location': 
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['location']}
                                }
                            ]
                           },
                           'Summary': 
                           {'title': 
                            [
                                {'text': 
                                 {'content':self.properties['summary']}
                                }
                            ]
                           },
                           'googleId':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['googleId']}
                                }
                            ]
                           },
                           'googleCreated':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['googleCreated']}
                                }
                            ]
                           },
                           'googleUpdated':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['googleUpdated']}
                                }
                            ]
                           },
                           'recurringEventId':
                           {'rich_text': 
                            [
                                {'text': 
                                 {'content':self.properties['recurringEventId']}
                                }
                            ]
                           }
                          },
            'archived':False
        }
        url = f'https://api.notion.com/v1/pages/{self.properties["notionId"]}'
        r = requests.patch(url, headers=self.headers, json=payload)
        self.properties['notionId'] = r.json()['id']
        self.properties['notionCreated'] = r.json()['created_time']
        self.properties['notionUpdated'] = r.json()['last_edited_time']
        return r

    def deleteNotionPage(self,NotionPageId=""):
        if NotionPageId=="":
            NotionPageId=self.properties["notionId"]
        try:
            url = f'https://api.notion.com/v1/blocks/{NotionPageId}'
            r = requests.delete (url, headers=self.headers)
        except:
            logger.error ('unable to delete notion page')
        return r

    def getGoogleInstances (self, service, google_calendar_id,time_min_days=1,time_max_days=1):
        return get_google_instances (service, calendarId=google_calendar_id['id'], eventId=self.properties['googleId'],timeMinDays=time_min_days, timeMaxDays=time_max_days)

    def matchedGoogleEvents(self, compareCalendar):
        # returns list of events
        matchedEventList = []
        if self.properties['googleId'] == "":
            return []
        for matchedEvents in [x for x in compareCalendar.allProperties() if ((x['googleId'] == self.properties['googleId']) or (x['recurringEventId'] == self.properties['googleId']))]:
            matchedEventList.append(matchedEvents)
        return matchedEventList """