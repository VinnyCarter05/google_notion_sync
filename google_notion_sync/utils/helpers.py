from datetime import datetime, timedelta
import logging
import pickle

from pytz import timezone

logger = logging.getLogger(__name__)

def as_list (variable):
    if type (variable)!= list:
        variable = [variable]
    return variable

# returns date time of date (days + current date) starting at midnight
# for days ago, make days negative
def datetime_from_now (days = 0):
    eastern = timezone('US/Eastern')
    now = datetime.now(eastern)
    logger.info (f"now = {now} now+timedelta = {now + timedelta(days=days)}")
    return (now + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)#.isoformat()

def event_start_datetime (event):
    eastern = timezone('US/Eastern')
    try:
        dt = datetime.fromisoformat((event.properties['start']).rstrip('Z')).replace(tzinfo=eastern)
        return dt
    except:
        return None

def event_end_datetime (event):
    eastern = timezone('US/Eastern')
    try:
        dt = datetime.fromisoformat((event.properties['end']).rstrip('Z')).replace(tzinfo=eastern)
        return dt
    except:
        return None        

def pickle_load(pickle_file):
    with open(pickle_file, "rb") as f:
        return pickle.load(f)

def pickle_save(obj, pickle_file_path):
    with open (pickle_file_path,"wb") as f:
        pickle.dump(obj,f)
    return