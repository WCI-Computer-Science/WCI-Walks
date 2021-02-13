import requests, datetime
from application.models import oauth, database
from application.templates.utils import add_to_total

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
    ).json()
    try:
        val = round(res["bucket"][0]["dataset"][0]["point"][0]["value"][0]["fpVal"]/1000, 2)
    except:
        val = 0
    return val

def autoload_day(userid, username, date, cur):
    distance = get_day_distance(userid, date)
    add_to_total(distance)
    walk = cur.execute(
            "SELECT * FROM walks WHERE id=%s AND walkdate=%s LIMIT 1;",
            (userid, date)
        )
    if walk:
        cur.execute(
            "UPDATE users SET distance=distance+%s WHERE id=%s",
            (distance, userid)
        )
        cur.execute(
            "UPDATE walks SET distance=distance+%s WHERE id=%s AND walkdate=%s LIMIT 1;",
            (distance, userid)
        )
    else:
        cur.execute(
            "UPDATE users SET distance=distance+%s WHERE id=%s",
            (distance, userid)
        )
        cur.execute(
            """
                INSERT INTO walks (id, username, distance, walkdate, trackedwithfit)
                VALUES (%s, %s, %s, %s, TRUE);
            """,
            (userid, username, distance, date),
        )

def autoload_day_all(date): # Autoload all users with google fit connected
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT userid, username, googlefit FROM users;")
        users = cur.fetchall()
        for userid, username, googlefit in users:
            if googlefit:
                dist = autoload_day(userid, username, date, cur)
    
    db.commit()
