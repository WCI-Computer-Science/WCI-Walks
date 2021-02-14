import requests, datetime
from application.models import oauth, database

def get_day_distance(userid, date): #date should be datetime.date object
    access_token = oauth.refresh_access_token(oauth.get_refresh(userid))
    start_time = int(datetime.datetime.combine(date, datetime.datetime.min.time()).timestamp())*1000
    end_time = start_time + 86400000
    res = requests.post(
        "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + access_token
        },
        json={
            "aggregateBy": [{
                "dataTypeName": "com.google.distance.delta",
                "dataSourceId": "derived:com.google.distance.delta:com.google.android.gms:platform_distance_delta"
            }],
            "bucketByTime": { "durationMillis": 86400000 },
            "startTimeMillis": start_time,
            "endTimeMillis": end_time
        }
    )
    print(res.text)
    res = res.json()
    try:
        val = round(res["bucket"][0]["dataset"][0]["point"][0]["value"][0]["fpVal"]/1000, 1)
    except:
        val = 0
    return val
