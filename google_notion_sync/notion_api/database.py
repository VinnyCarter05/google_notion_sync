# Notion database functions

import asyncio
from http.client import responses
import logging
from urllib import response
import aiohttp
import requests

from google_notion_sync.classes.event import Event

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s',filename='./logs/example.log', filemode='w')
logger = logging.getLogger(__name__)

def notion_query_database (database_id, headers, payload=""):
    # gests a list of pages contained in the database
    #headers in form headers = {"Authorization": f"Bearer {NOTION_API_KEY}", "Content-Type": "application/json", "Notion-Version": "2021-08-16"}
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    try:
        if payload:
            r = requests.post (url, json=payload, headers=headers)
        else:
            r = requests.post (url, headers=headers)
        return (r)
    except:
        logger.error (f'Error querying notion database with datatbase_id = {database_id}')
        return None

def notion_retrieve_page (headers, event_id):
    url = f'https://api.notion.com/v1/pages/{event_id}'
    try:
        r = requests.get (url, headers=headers)
        return (r)
    except:
        logger.error(f'Error retrieving notion page with event_id = {event_id}')
        return None
 
async def async_notion_retrieve_page (session, headers, event_id):
    url = f'https://api.notion.com/v1/pages/{event_id}'
    async with session.get(url, headers=headers) as response:
        try:
            notion_page = await response.json()
        except:
            logger.error(f'Error retrieving notion page with event_id = {event_id}') 
            return None
        logger.info(f"notion_page = {notion_page}")
        notion_event = Event(notion_page=notion_page)
        return notion_event

def notion_delete_page(headers, notion_page_id):
    url = f'https://api.notion.com/v1/blocks/{notion_page_id}'
    try:
        r = requests.delete (url, headers=headers)
        return r
    except:
        logger.error (f'unable to delete notion page with notion_page_id = {notion_page_id}')
        return None

async def async_notion_delete_page(session, headers, notion_page_id):
    url = f'https://api.notion.com/v1/blocks/{notion_page_id}'
    try:
        response = await session.delete(url, headers=headers)
        return response
    except:
        logger.error (f'unable to delete notion page with notion_page_id = {notion_page_id}')
        return None

async def async_notion_delete_pages(headers, notion_page_ids):
    async with aiohttp.ClientSession() as session:
        all_responses = []
        for notion_page_id in notion_page_ids:
            print (notion_page_id)
            response = asyncio.ensure_future(async_notion_delete_page(session=session,headers=headers,notion_page_id=notion_page_id))
            if response != None:
                all_responses.append(response)
        return await asyncio.gather(*all_responses)