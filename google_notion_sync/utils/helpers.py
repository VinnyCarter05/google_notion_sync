import datetime

def as_list (variable):
    if type (variable)!= list:
        variable = [variable]
    return variable

# returns date time of date (days + current date)
# for days ago, make days negative
def datetime_from_now (days = 0):
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now +datetime.timedelta(days=days)).isoformat()