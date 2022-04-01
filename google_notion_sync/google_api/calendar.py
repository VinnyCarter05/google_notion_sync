import os
import json
import logging

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload #, MediaIoBaseDownload

from google_notion_sync.google_api.drive import google_drive_download_file, replaceFileGoogleDrive
from google_notion_sync.utils.helpers import datetime_from_now

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

def get_google_calendar_service(creds):
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        logger.error('An error occurred: %s' % error)
        return None

def get_google_instances (service, calendar_id, event_id, pageToken = None):#, timeMin=None,timeMax=None):
    all_events = []
    last_page = False
    events = None
    nextSyncToken = None
    while not last_page:
        try:
            events = service.events().instances(calendarId=calendar_id, eventId=event_id, pageToken = pageToken).execute()
        except:
            logger.error(f"error calling service.events().instances(calendarId={calendar_id}, eventId={event_id}, pageToken = {pageToken}).execute()")
            return all_events, nextSyncToken
        for item in events['items']:
            if item['status'] == "confirmed":
                item['status'] = "confirmed - instance"
            all_events.append(item)
        if 'nextPageToken' in events.keys():
            pageToken =events['nextPageToken'] 
        else:
            last_page = True
        if 'nextSyncToken' in events.keys():
            nextSyncToken = events['nextSyncToken']
    return all_events, nextSyncToken

def get_all_google_calendars (service):
    all_google_calendars = []
    try:
        items = service.calendarList().list().execute()['items']
    except:
        logger.error ('error in retrieving google calendar list')
        return all_google_calendars
    for item in items:
        calendar_item = {'id':item['id'],'summary':item['summary']}
        all_google_calendars.append (calendar_item)
    return all_google_calendars

def google_calendar_events_list(calendar_service, calendar_id, page_token = None, sync_token = None):#, timeMax = None, timeMin = None):
    events = None
    error_ = 0
    try:
        events = calendar_service.events().list(calendarId=calendar_id,pageToken=page_token,syncToken=sync_token).execute()
        return events, error_
    except HttpError as error:
    #           // A 410 status code, "Gone", indicates that the sync token is invalid.
        if error.status_code == 410:
            logger.error ("Invalid sync token, clearing event store and re-syncing")
            return None, error.status_code
        else:
            logger.error ('error:', error)
            return None, error.status_code
    except:
        logger.error ('error:', error)
        return None, error.status_code
    
def google_calendar_sync_events_list(service, drive_service, google_drive_fileId="", calendar_id='primary',resync=False):#,timeMinDays=1,timeMaxDays=1):
    # timeMin = datetime_from_now(-timeMinDays)
    # timeMax = datetime_from_now(timeMaxDays)
    all_events = []
    #     // Load the sync token stored from the last execution, if any.
    logger.warning("google_calendar_sync_events_list")
    sync_token = None
    sync_tokens = {}
    st_file_name = './google_notion_sync/config/synctoken.json'
    if drive_service!="" and google_drive_fileId!="":
        try:
            fiahl = google_drive_download_file(drive_service,st_file_name,google_drive_fileId) 
        except:
            logger.error ('unable to download synctoken from googleDrive')
    if os.path.exists (st_file_name):
        with open (st_file_name,"r") as f:
            sync_tokens = json.load(f)
            logger.info(f"sync_tokens: {sync_tokens}")
        if calendar_id in sync_tokens.keys():
            if resync:
                sync_tokens.pop(calendar_id)
                logger.info(f"resync: \npopped sync_tocken:{calendar_id}; now sync_tokens: {sync_tokens}")
            else:
                sync_token = sync_tokens[calendar_id]
                logger.info(f"not resync")
    if sync_token == None:
        logger.info ("Performing full sync.")
    else:
        logger.info ("Performing incremental sync.")

    #     // Retrieve the events, one page at a time.
    page_token = None
    last_page = False
    events = None
    while not last_page:
        logger.info(f"google_calendar_events_list call with parameters: page_token = {page_token}, sync_token = {sync_token}")
        events, error_ = google_calendar_events_list(service, calendar_id, page_token = page_token, sync_token = sync_token)#, timeMax = timeMax, timeMin = timeMin)
    #           // A 410 status code, "Gone", indicates that the sync token is invalid.
        if error_ == 410:
            logger.warning ("Invalid sync token, clearing event store and re-syncing")
            sync_tokens.pop(calendar_id)
            with open(st_file_name,"w") as f:
                json.dump(sync_tokens,f)
            logger.info ("Uploading file " + st_file_name + "...")

            #We have to make a request hash to tell the google API what we're giving it
            body = {'name': st_file_name, 'parents': ['0B1zaytT0-pD-em5jWnYwT2dCRG8'], 'mimeType': 'application/vnd.google-apps.file'}

            #Now create the media file upload object and tell it what file to upload,
            #in this case 'test.html'
            media = MediaFileUpload('synctoken.json', mimetype = 'text/plain')

            #Now we're doing the actual post, creating a new file of the uploaded type
            fiahl = drive_service.files().create(body=body, media_body=media).execute()
            os.remove(st_file_name) #? need to remove
            sync_token = None
            all_events = google_calendar_sync_events_list(service,drive_service, google_drive_fileId=google_drive_fileId, calendarId=calendar_id,resync=resync)#,timeMinDays=timeMinDays,timeMaxDays=timeMaxDays)
            return all_events
        elif error_ > 0:
            logger.error ('error:', error_)
            return
        items = events['items']
        if len(items) == 0:
            logger.info ("No new events to sync.")
            last_page=True
        else:
            for event in items:
                logger.warning(f"event = {event}")
                event['calendar'] = calendar_id
                logger.warning(f"new event = {event}")
                all_events.append(event)
            if 'nextPageToken' in events.keys():
                page_token = events['nextPageToken']
            else:
                page_token = None
        if page_token == None:
            last_page = True

    google_instances = []
    for num, google_trial_event in enumerate(all_events):
        logger.warning (f"{num}, googe_trial_event = {google_trial_event}")
        google_instances.append(google_trial_event)
        if google_trial_event['status'] == 'cancelled':
            logger.warning (f"{num} cancelled so google_trial_event = {google_trial_event}")
        else:
            try:
                google_instance, nextSyncToken = get_google_instances(service,google_trial_event['calendar'], google_trial_event['id'])
                google_instances.extend(google_instance)
                logger.warning (f"{num} instances recurring: {google_instance}")
            except:
                logger.warning (f"{num} error non-recurring: {google_trial_event}")
    #     // Store the sync token from the last request to be used during the next execution.
    if events['nextSyncToken']!= None:
        sync_token = events['nextSyncToken']
        logger.info(f"nextSyncToken={sync_token}")
        sync_tokens[calendar_id]=sync_token
        logger.info(f"new sync_tokens={sync_tokens}")
        with open(st_file_name,"w") as f:
            json.dump(sync_tokens, f)
        fiahl = replaceFileGoogleDrive(drive_service,st_file_name,google_drive_fileId,'application/json')
    return google_instances #all_events

