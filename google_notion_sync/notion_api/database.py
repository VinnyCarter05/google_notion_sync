# Notion database functions

import requests

def notion_query_database (database_id, headers="", payload=""):
    # gests a list of pages contained in the database
    #headers in form headers = {"Authorization": f"Bearer {NOTION_API_KEY}", "Content-Type": "application/json", "Notion-Version": "2021-08-16"}
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    try:
        r = requests.post (url, json=payload, headers=headers)
        return (r)
    except:
        print ('Error querying notion database')
        return None

def notion_retrieve_page (headers, event_id):
    url = f'https://api.notion.com/v1/pages/{event_id}'
    try:
        r = requests.get (url, headers=headers)
        return (r)
    except:
        print ('Error retrieving notion page')
    return None