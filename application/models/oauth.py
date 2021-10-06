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
            "redirect_uri": "https://wciwalks.herokuapp.com/" + "users/authorize/confirmlogin" #TODO: GET ROOT URL THAT DOESN'T REQUIRE REQUEST CONTEXT
        } # HARDCODING FOR NOW
    )
    res = res.json()
    return res["access_token"]


def get_refresh(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT refreshtoken FROM users WHERE id=%s;",
            (userid,)
        )
        result = cur.fetchone()[0]
    return result



# For connecting to walk API. Currently: Strava
def walkapi_get_auth_url():
    auth_url = ("https://www.strava.com/oauth/authorize" +
        "?client_id=" + current_app.config["WALKAPI_CLIENT_ID"] +
        "&redirect_uri=" + request.url_root + "users/authorizewalk/confirmlogin" +
        "&response_type=code"
    )
    auth_url += "&scope=" + current_app.config["WALKAPI_SCOPES"][0]
    for i in range(1, len(current_app.config["WALKAPI_SCOPES"])):
        auth_url += "," + current_app.config["WALKAPI_SCOPES"][i]

    return auth_url


def walkapi_get_access_token(auth_code):
    res = requests.post(
        "https://www.strava.com/oauth/token",
        json={
            "code": auth_code,
            "client_id": current_app.config["WALKAPI_CLIENT_ID"],
            "client_secret": current_app.config["WALKAPI_CLIENT_SECRET"],
            "grant_type": "authorization_code",
        }
    )
    res = res.json()
    return res["access_token"], res.get("refresh_token"), res["expires_at"]


def walkapi_refresh_access_token(refresh, cur):
    print("refresh access token")
    res = requests.post(
        "https://www.strava.com/oauth/token",
        json={
            "refresh_token": refresh,
            "client_id": current_app.config["WALKAPI_CLIENT_ID"],
            "client_secret": current_app.config["WALKAPI_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "redirect_uri": "https://wciwalks.herokuapp.com/" + "users/authorizewalk/confirmlogin" #TODO: GET ROOT URL THAT DOESN'T REQUIRE REQUEST CONTEXT
        } # HARDCODING FOR NOW
    )
    res = res.json()
    access, refresh, expires_at = res["access_token"], res["refresh_token"], res["expires_at"]

    cur.execute(
        "UPDATE users SET walkapi_accesstoken=%s, walkapi_refreshtoken=%s, walkapi_expiresat=%s",
        (access, refresh, expires_at)
    )

    return access


def walkapi_get_refresh(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT walkapi_refreshtoken FROM users WHERE id=%s;",
            (userid,)
        )
        result = cur.fetchone()[0]
    return result


# Return a valid access code, and update the database if a refresh is necessary
def walkapi_get_access(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT walkapi_accesstoken, walkapi_refreshtoken, walkapi_expiresat FROM users WHERE id=%s",
            (userid,)
        )
        result = cur.fetchone()
        access, refresh, expiresat = result[0], result[1], result[2]
        if int(datetime.datetime.now().timestamp()) > expiresat - 300:
            access = walkapi_refresh_access_token(refresh, cur)
            db.commit()
    
    return access


# Delete tokens from user and disconnect them from walk API
def walkapi_disconnect(userid, cur):
    print("DISCONNECT WALKAPI")
    cur.execute(
        """
        UPDATE users SET
        walkapi_accesstoken=NULL,
        walkapi_refreshtoken=NULL,
        walkapi_expiresat=NULL,
        googlefit=false
        WHERE id=%s
        """,
        (userid,)
    )



# For backup authentication service. Currently: auth0.com
def backup_get_auth_url():
    auth_url = ("https://dev-aicygucs.us.auth0.com/authorize" +
        "?client_id=" + current_app.config["BACKUP_CLIENT_ID"] +
        "&redirect_uri=" + request.url_root + "users/authorize/confirmlogin" +
        "&response_type=code" +
        "&access_type=offline"
    )
    auth_url += "&scope=" + current_app.config["BACKUP_OAUTH_SCOPES"][0]
    for i in range(1, len(current_app.config["BACKUP_OAUTH_SCOPES"])):
        auth_url += "%20" + current_app.config["BACKUP_OAUTH_SCOPES"][i]

    return auth_url

def backup_get_access_token(auth_code):
    res = requests.post(
        "https://dev-aicygucs.us.auth0.com/oauth/token",
        json={
            "code": auth_code,
            "client_id": current_app.config["BACKUP_CLIENT_ID"],
            "client_secret": current_app.config["BACKUP_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "redirect_uri": request.url_root + "users/authorize/confirmlogin"
        }
    )
    res = res.json()
    return res["access_token"], res.get("refresh_token")

def backup_get_id_info(access_token):
    res = requests.post(
        "https://dev-aicygucs.us.auth0.com/userinfo",
        headers={
            "Content-length": "0",
            "Content-type": "application/json",
            "Authorization": "Bearer " + access_token
        }
    )
    return res.json()

def backup_refresh_access_token(refresh):
    res = requests.post(
        "https://dev-aicygucs.us.auth0.com/oauth/token",
        json={
            "refresh_token": refresh,
            "client_id": current_app.config["BACKUP_CLIENT_ID"],
            "client_secret": current_app.config["BACKUP_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "redirect_uri": "https://wciwalks.herokuapp.com/" + "users/authorize/confirmlogin" #TODO: GET ROOT URL THAT DOESN'T REQUIRE REQUEST CONTEXT
        } # HARDCODING FOR NOW
    )
    res = res.json()
    return res["access_token"]