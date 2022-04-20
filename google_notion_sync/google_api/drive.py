import logging
import io

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

def get_google_drive_service(creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        logger.error('An error occurred: %s' % error)
        return None

def google_drive_file_upload (service, upload_file, drive_file_name, folder, mimetype):
    logger.info ("Uploading file " + upload_file + " as " + drive_file_name)
    
    #We have to make a request hash to tell the google API what we're giving it
    body = {
        'name': drive_file_name, 
        'parents': [folder]
        }
        #, 'mimeType': 'application/json'}
    #Now create the media file upload object and tell it what file to upload,
    #in this case 'test.html'
    media = MediaFileUpload(upload_file, mimetype = mimetype)
    
    #Now we're doing the actual post, creating a new file of the uploaded type
    return service.files().create(body=body, media_body=media).execute()

def google_drive_replace_file(service, file_name, fileId, mimetype):
    logger.info ("Uploading file " + file_name + "...")
    media = MediaFileUpload(file_name, mimetype = mimetype)
    return service.files().update(fileId=fileId, media_body=media).execute()

def google_drive_download_file(service, file_name, fileId):
    request = service.files().get_media(fileId=fileId)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        logger.info ("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    with open(file_name,'wb') as f:
        f.write(fh.read())
        f.close()