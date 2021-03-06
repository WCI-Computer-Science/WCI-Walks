from datetime import date

from flask import current_app
from wtforms.validators import ValidationError

from application.models import database
from application.models.fitapi import get_day_distance


def get_all_time_leaderboard():
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT username, distance, wrdsbusername, position, id FROM users;")
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    userdistances = [[i[0], fancy_float(i[1]), i[2], i[3], i[4]] for i in userdistances]
    return userdistances


def get_day_leaderboard(date):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT username, distance, id FROM walks WHERE walkdate=%s;",
            (date,)
        )
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    userdistances = list(map(_convert_id_to_wrdsbusername, userdistances))
    userdistances = [[i[0], fancy_float(i[1]), i[2]] for i in userdistances]
    return userdistances


def get_credentials_from_wrdsbusername(wrdsbusername, cur=None):
    if cur is None:
        closecur = True
        db = database.get_db()
        cur = db.cursor()
    else:
        closecur = False
    cur.execute(
        "SELECT id, username FROM users WHERE wrdsbusername=%s LIMIT 1;",
        (wrdsbusername,),
    )
    user = cur.fetchone()
    if closecur:
        cur.close()
    return user[0], user[1]


def get_wrdsbusername_from_id(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT wrdsbusername FROM users WHERE id=%s LIMIT 1;",
            (userid,)
        )
        return cur.fetchone()[0]


def _convert_id_to_wrdsbusername(leaderboarddata):
    leaderboarddata[2] = get_wrdsbusername_from_id(leaderboarddata[2])
    return leaderboarddata


def isadmin(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT wrdsbusername, valid FROM admins WHERE id=%s;",
            (userid,)
        )
        row = cur.fetchone()
    return (
        row[0] == get_wrdsbusername_from_id(userid)
        and row[1] if row is not None else False
    )


def isblacklisted(userid, email):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT wrdsbusername, valid FROM blacklist WHERE id=%s;",
            (userid,)
        )
        result = cur.fetchone()
        if result is None:
            cur.execute(
                "SELECT id, valid FROM blacklist WHERE wrdsbusername=%s;",
                (email.split("@")[0],),
            )
            result = cur.fetchone()
    return (
        result[0] in [userid, email.split("@")[0]] and result[1]
        if result is not None
        else False
    )

def haspayed(email):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM payed WHERE email=%s;", (email,)
        )
        return cur.fetchone() != None

def walk_will_max_distance(distance, id):
    curdistance = _get_walk_distance(id)
    return (distance + curdistance) > 42 or (distance + curdistance) < 0

def cap_distance(distance, id):
    curdistance = _get_walk_distance(id)
    return (42-curdistance if distance>0 else curdistance*-1) if walk_will_max_distance(distance, id) else distance

def _get_walk_distance(id):
    db = database.get_db()
    walkdate = date.today()
    with db.cursor() as cur:
        cur.execute(
            "SELECT distance FROM walks WHERE walkdate=%s AND id=%s LIMIT 1;",
            (
                walkdate,
                id,
            ),
        )
        walk = cur.fetchone()
        if walk is not None:
            return int(walk[0])
        else:
            return 0


def walk_is_maxed(id, max=42):
    def _walk_is_maxed(form, field):
        if _get_walk_distance(id) >= max:
            raise ValidationError(
                "You can only walk between 0 and " + str(max) + " per day."
            )

    return _walk_is_maxed


def update_total():
    print("Starting to update user totals.")
    db = database.get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE users u
                SET distance=t.d
                FROM (
                    SELECT id, SUM(distance) d
                    FROM walks
                    GROUP BY id
                ) t
                WHERE u.id=t.id;
                """
            )
            cur.execute("DELETE FROM walks WHERE distance=0;")
        db.commit()
        print("Done updating user totals.\nStarting to update global total!")
        with db.cursor() as cur:
            cur.execute("UPDATE total SET distance=t.d FROM (SELECT SUM(distance) d FROM users) t;")
        db.commit()
    except:
        print("Something went wrong")
    print("Done updating totals!")
    return True


def add_to_total(num, cur):
    cur.execute("UPDATE total SET distance=distance+%s", (num,))

def fancy_float(n):
    try:
        n = float(n)
        if n % 1 == 0:
            return int(n)
        return n
    except ValueError:
        return 0
"""
def replace_walk_distances(distances, dates, olddistances, user, id):
    db = database.get_db()
    with db.cursor() as cur:
        for i in range(len(dates)):
            if distances[i] != olddistances[i]:
                user.update_walk(
                    distances[i],
                    dates[i],
                    None,
                    cur,
                    replace=True,
                    id=id
                )
                print(
                    "Updated",
                    user.id,
                    "walk on",
                    dates[i],
                    "to be",
                    distances[i]
                )
    db.commit()"""

def update_leaderboard_positions():
    db = database.get_db()
    leaderboard = get_all_time_leaderboard()
    with db.cursor() as cur:
        for i in range(len(leaderboard)):
            if leaderboard[i][3]!=i+1 and leaderboard[i][1]>0:
                cur.execute(
                    "UPDATE users SET position=%s WHERE id=%s;",
                    (i+1, leaderboard[i][4])
                )
            elif leaderboard[i][3]!=None and leaderboard[i][1]<=0:
                cur.execute(
                    "UPDATE users SET position=null WHERE id=%s;",
                    (leaderboard[i][4],)
                )
    db.commit()

def verify_walk_form(form, id):
    try:
        float(form.distance.data)
    except ValueError:
        return "Please submit a number."
    walkdistance = _get_walk_distance(id)
    if walkdistance>=42 and int(form.distance.data)>0:
        return "You can only go up to 42 km per day!"
    if walkdistance<=0 and float(form.distance.data)<0:
        return "You can't go less that 0 km per day!"
    return True

def get_edit_distance_data(wrdsbusername):
    userid, username = get_credentials_from_wrdsbusername(wrdsbusername)
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT walkdate, distance, trackedwithfit FROM walks WHERE id=%s;", (userid,)
        )
        allwalks = cur.fetchall()
        allwalks.sort(key=lambda row: row[0])
    return allwalks

def edit_distance_update(distance, date, wrdsbusername):
    userid, username = get_credentials_from_wrdsbusername(wrdsbusername)
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT distance FROM walks WHERE id=%s AND walkdate=%s;",
            (userid, date)
        )
        olddistance = float(cur.fetchone()[0])
        if olddistance != distance:
            distancechange = distance-olddistance
            cur.execute(
                "UPDATE walks SET distance=%s, trackedwithfit=False WHERE id=%s AND walkdate=%s;",
                (distance, userid, date)
            )
            cur.execute(
                "UPDATE users SET distance=distance+%s WHERE id=%s;",
                (distancechange, userid)
            )
            add_to_total(distancechange, cur)
            db.commit()

def autoload_day(userid, username, date, cur):
    distance = get_day_distance(userid, date)
    cur.execute(
            "SELECT distance FROM walks WHERE id=%s AND walkdate=%s LIMIT 1;",
            (userid, date)
        )
    walk = cur.fetchone()
    if walk:
        if round(distance-float(walk[0]), 1) > 0:
            cur.execute(
                "UPDATE users SET distance=distance+%s WHERE id=%s;",
                (round(distance-float(walk[0]), 1), userid)
            )
            cur.execute(
                "UPDATE walks SET distance=%s WHERE id=%s AND walkdate=%s;",
                (round(distance, 1), userid, date)
            )
            add_to_total(distance-float(walk[0]), cur)
    elif round(distance, 1) > 0:
        cur.execute(
            "UPDATE users SET distance=distance+%s WHERE id=%s;",
            (round(distance, 1), userid)
        )
        cur.execute(
            """
                INSERT INTO walks (id, username, distance, walkdate, trackedwithfit)
                VALUES (%s, %s, %s, %s, TRUE);
            """,
            (userid, username, round(distance, 1), date),
        )
        add_to_total(distance, cur)

def autoload_day_all(date): # Autoload all users with google fit connected
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, username FROM users WHERE googlefit=True;")
        users = cur.fetchall()
        for userid, username in users:
            dist = autoload_day(userid, username, date, cur)
    db.commit()

def update_tick(context):
    with context:
        update_leaderboard_positions()

def medium_update_tick(context):
    with context:
        autoload_day_all(date.today())

def long_update_tick(context):
    with context:
        update_total()
