import sys, time
from application.models import database
from wtforms.validators import ValidationError
from datetime import date

def get_all_time_leaderboard():
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT username, distance, wrdsbusername FROM users;"
        )
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)

    return userdistances

def get_day_leaderboard(date):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT username, distance, id FROM walks WHERE walkdate=%s;", (date,)
        )
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    userdistances = list(map(_convert_id_to_wrdsbusername, userdistances))
    return userdistances

def get_credentials_from_wrdsbusername(wrdsbusername, cur=None):
    if cur == None:
        closecur = True
        db = database.get_db()
        cur = db.cursor()
    else:
        closecur = False
    cur.execute(
            "SELECT id, username FROM users WHERE wrdsbusername=%s LIMIT 1;", (wrdsbusername,)
    )
    user = cur.fetchone()
    if closecur: cur.close()
    return user[0], user[1]

def get_wrdsbusername_from_id(userid):
    db = database.get_db()
    with db.cursor() as cur:
         cur.execute(
             "SELECT wrdsbusername FROM users WHERE id=%s LIMIT 1;", (userid,)
         )
         return cur.fetchone()[0]

def _convert_id_to_wrdsbusername(leaderboarddata):
    leaderboarddata[2] = get_wrdsbusername_from_id(leaderboarddata[2])
    return leaderboarddata

def isadmin(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT wrdsbusername, adminvalid FROM admins WHERE id=%s;", (userid,)
        )
        row = cur.fetchone()
    return (row[0]==get_wrdsbusername_from_id(userid) and row[1] if row!=None else False)

def walk_will_max_distance(distance, id):
    curdistance = _get_walk_distance(id)
    return (distance + curdistance)>42

def _get_walk_distance(id):
    db = database.get_db()
    walkdate = date.today()
    with db.cursor() as cur:
        cur.execute(
            "SELECT distance FROM walks WHERE walkdate=%s AND id=%s LIMIT 1;", (walkdate, id,)
        )
        walk = cur.fetchone()
        if walk!= None:
            return int(walk[0])
        else:
            return 0

def walk_is_maxed(id, max=42):
    def _walk_is_maxed(form, field):
        if _get_walk_distance(id)>=max:
            raise ValidationError("You can only walk between 0 and "+str(max)+" per day.")
    return _walk_is_maxed

def _get_index_zero_of_list(item):
    return item[0]

def update_total():
    print("Starting to update user totals.")
    db = database.get_db()
    if not is_blocked():
        start_blocking()
    else:
        raise Exception("Already Blocked") # Need to figure out what to do here
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, distance FROM walks;"
            )
            distances = {}
            for i in cur.fetchall():
                if i[0] in distances.keys():
                    distances[i[0]] += float(i[1])
                else:
                    distances[i[0]] = float(i[1])
            for i in distances.keys():
                cur.execute(
                    "UPDATE users SET distance=%s WHERE id=%s;", (distances[i], i,)
                )
                cur.execute(
                    "SELECT * FROM users WHERE id=%s;", (i,)
                )
        print("Done updating user totals.\nStarting to update global total!")
        with db.cursor() as cur:
            cur.execute(
                "SELECT distance FROM users;"
            )
            originaltotal = get_total()
            allusers = cur.fetchall()
        sub_from_total(originaltotal-sum(map(float, map(_get_index_zero_of_list, allusers))))
        db.commit()
    finally:
        stop_blocking()
    print("Done updating totals!")

def get_total():
    global total
    return total

def set_total(num):
    global total
    total = num
    db_commit_total()
    return total

def add_to_total(num):
    global total
    total += num
    db_commit_total()
    return total

def sub_from_total(num):
    global total
    total -= num
    db_commit_total()
    return total

def db_get_total():
    global total
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM total;"
        )
        total = cur.fetchone()[0]
    return total

def db_commit_total():
    global total
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM total;"
        )
        if cur.fetchone()==None:
            cur.execute(
                "INSERT INTO total (distance) VALUES (%s);", (round(total, 1),)
            )
        else:
            cur.execute(
                "UPDATE total SET distance=%s", (round(total, 1),)
            )
    db.commit()
    return total

def is_blocked():
    global block
    return block

def stop_blocking():
    global block
    block = False
    return block

def start_blocking():
    global block
    block = True
    return block

def fancy_float(n):
    n = float(n)
    if n%1==0:
        return int(n)
    return float(n)

def replace_walk_distances(distances, dates, olddistances, user, id):
    db = database.get_db()
    with db.cursor() as cur:
        for i in range(len(dates)):
            if distances[i]!=olddistances[i]:
                user.update_walk(distances[i], dates[i], None, cur, replace=True, id=id)
                print("Updated", user.id, "walk on", dates[i], "to be", distances[i])
    db.commit()

total = 0
db_get_total()
block = False
