# app to sync google calendar to notion calendar
# .env file contains notion database id
import os

from dotenv import load_dotenv

def run():
    load_dotenv()
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')