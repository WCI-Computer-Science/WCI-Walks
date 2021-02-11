from datetime import date

from flask import current_app
from wtforms.validators import ValidationError

from application.models import database


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


def walk_will_max_distance(distance, id):
    curdistance = _get_walk_distance(id)
    return (distance + curdistance) > 42


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
    database.start_blocking()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, distance FROM walks;")
            distances = {}
            for i in cur.fetchall():
                if i[0] in distances.keys():
                    distances[i[0]] += i[1]
                else:
                    distances[i[0]] = i[1]
            for i in distances.keys():
                cur.execute(
                    "UPDATE users SET distance=%s WHERE id=%s;",
                    (distances[i], i)
                )
            cur.execute("DELETE FROM walks WHERE distance=0;")
        db.commit()
        print("Done updating user totals.\nStarting to update global total!")
        with db.cursor() as cur:
            print("ok1")
            cur.execute("SELECT distance FROM users;")
            print("ok2")
            newtotal = sum(i["distance"] for i in cur.fetchall())
            set_total(newtotal, cur)
        db.commit()
    finally:
        database.stop_blocking()
    print("Done updating totals!")
    return True


def get_total():
    global total
    return total


def set_total(num, cur):
    global total
    total = num
    db_write_total(cur)
    return total


def add_to_total(num, cur):
    global total
    total += num
    db_write_total(cur)
    return total


def db_get_total():
    global total
    db = database.get_db()
    with db.cursor() as cur:
        total = database.get_total(cur)
    if total:
        total = total["distance"]
    else:
        total = 0
    return total


def db_write_total(cur):
    global total
    cur.execute("SELECT * FROM total;")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO total (distance) VALUES (%s);",
            (round(total, 1),)
        )
    else:
        cur.execute("UPDATE total SET distance=%s", (round(total, 1),))
    return total


def fancy_float(n):
    try:
        n = float(n)
        if n % 1 == 0:
            return int(n)
        return n
    except ValueError:
        return 0


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
    db.commit()

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

def update_tick():
    update_leaderboard_positions()

def long_update_tick():
    pass

total = 0
if not current_app.config["DONT_LOAD_DB"]:
    db_get_total()
