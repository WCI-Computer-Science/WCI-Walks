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

def get_name_from_id(userid):
    db = database.get_db()
    with db.cursor() as cur:
         cur.execute(
             "SELECT username FROM users WHERE id=%s;", (userid,)
         )
         return cur.fetchone()[0]

def get_name_from_wrdsbusername(username):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT username FROM users WHERE wrdsbusername=%s;", (username,)
        )
        return cur.fetchone()[0]

def get_id_from_wrdsbusername(username):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id FROM users WHERE wrdsbusername=%s;", (username,)
        )
        return cur.fetchone()[0]

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
