import requests, datetime
from application.models import oauth, database

def get_day_distance(userid, date, cur): #date should be datetime.date object
    access_token = oauth.walkapi_get_access(userid)
    start_time = int(datetime.datetime.combine(date, datetime.datetime.min.time()).timestamp())
    end_time = start_time + 86400
    res = requests.get(
        "https://www.strava.com/api/v3/athlete/activities?after=" + str(start_time) + "&before=" + str(end_time) + "&per_page=128",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + access_token
        }
    )
    res = res.json()
    val = 0
    try:
        for r in res:
            val += r["distance"]/1000
        val = round(val, 1)
    except:
        print("Error fetching distance. Returned result: ")
        print(res)
        oauth.walkapi_disconnect(userid, cur)
    return val
