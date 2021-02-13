import requests, datetime
from flask import current_app, g, request, session
from application.models import database

def get_auth_url():
    auth_url = ("https://accounts.google.com/o/oauth2/v2/auth" +
        "?client_id=" + current_app.config["GOOGLE_CLIENT_ID"] +
        "&redirect_uri=" + request.url_root + "users/authorize/confirmlogin" +
        "&response_type=code" +
        "&access_type=offline"
    )
    auth_url += "&scope=" + current_app.config["OAUTH_SCOPES"][0]
    for i in range(1, len(current_app.config["OAUTH_SCOPES"])):
        auth_url += "%20" + current_app.config["OAUTH_SCOPES"][i]

    return auth_url

def get_access_token(auth_code):
    res = requests.post(
        "https://oauth2.googleapis.com/token",
        json={
            "code": auth_code,
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "redirect_uri": request.url_root + "users/authorize/confirmlogin"
        }
    )
    res = res.json()
    return res["access_token"], res.get("refresh_token")

def get_id_info(access_token):
    res = requests.post(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={
            "Content-length": "0",
            "Content-type": "application/json",
            "Authorization": "Bearer " + access_token
        }
    )
    return res.json()

def refresh_access_token(refresh):
    res = requests.post(
        "https://oauth2.googleapis.com/token",
        json={
            "refresh_token": refresh,
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "redirect_uri": request.url_root + "users/authorize/confirmlogin"
        }
    )
    return res.text


def get_refresh(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT refreshtoken FROM users WHERE id=%s;",
            (userid,)
        )
        result = cur.fetchone()[0]
    return result

def autoload_day(userid, date): #date should be datetime.date object
    access_token = refresh_access_token(get_refresh(userid))
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