import sys
from application.models import database

def get_all_time_leaderboard():
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT username, distance, wrdsbusername FROM users;"
        )
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)

    return userdistances[:15]

def get_day_leaderboard(date):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT username, distance, id FROM walks WHERE walkdate=%s;", (date,)
        )
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    userdistances = list(map(_convert_id_to_wrdsbusername, userdistances))
    return userdistances[:10]

# Do we need this function? If we had access to a user's id we would probably have access to their name too
def get_name_from_id(userid):
    db = database.get_db()
    with db.cursor() as cur:
         cur.execute(
             "SELECT username FROM users WHERE id=%s;", (userid,)
         )
         return cur.fetchone()[0]

# Only one database query if we have only one function
def get_credentials_from_wrdsbusername(wrdsbusername, cur):
    cur.execute(
            "SELECT id, username FROM users WHERE wrdsbusername=%s LIMIT 1;", (wrdsbusername,)
    )
    user = cur.fetchone()
    return user[0], user[1]

def get_wrdsbusername_from_id(userid):
    db = database.get_db()
    with db.cursor() as cur:
         cur.execute(
             "SELECT wrdsbusername FROM users WHERE id=%s;", (userid,)
         )
         return cur.fetchone()[0]

def _convert_id_to_wrdsbusername(leaderboarddata):
    leaderboarddata[2] = get_wrdsbusername_from_id(leaderboarddata[2])
    return leaderboarddata
