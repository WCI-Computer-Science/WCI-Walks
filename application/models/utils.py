from datetime import date, timedelta
import time, json

from flask import current_app
import random, string
from wtforms.validators import ValidationError

from application.models import database
from application.models.fitapi import get_day_distance
from application.models import nouns, adjectives


def get_all_time_leaderboard():
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT username, distance, wrdsbusername, position, id FROM users;")
        userdistances = cur.fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    return [[i[0], fancy_float(i[1]), i[2], i[3], i[4]] for i in userdistances]


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
    return [[i[0], fancy_float(i[1]), i[2]] for i in userdistances]


def get_all_time_team_leaderboard():
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT teamname, distance, id FROM teams;")
        teamdistances = cur.fetchall()
    teamdistances.sort(key=lambda team: team[1], reverse=True)
    return [[i[0], fancy_float(i[1]), i[2]] for i in teamdistances]


#TODO: use caching to make this faster
def get_day_team_leaderboard(date):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT t.teamname, td.distance, t.id
            FROM teams t
            INNER JOIN (
                SELECT u.teamid teamid, SUM(w.distance) distance
                FROM users u
                INNER JOIN walks w
                ON u.id=w.id
                WHERE w.walkdate=%s
                GROUP BY u.teamid
            ) td
            ON t.id=td.teamid
            """,
            (date,)
        )
        teamdistances = cur.fetchall()
    teamdistances.sort(key=lambda team: team[1], reverse=True)
    return [[i[0], fancy_float(i[1]), i[2]] for i in teamdistances]


def get_announcements():
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, notice FROM announcements;")
        return cur.fetchall()


def get_multipliers(date=None):
    db = database.get_db()
    with db.cursor() as cur:
        if date:
            cur.execute("SELECT multiplydate, factor FROM multipliers WHERE multiplydate=%s", (date,))
            return cur.fetchone()
        else:
            cur.execute("SELECT multiplydate, factor FROM multipliers;")
            return cur.fetchall()


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
    return (distance + curdistance) > 300 or (distance + curdistance) < 0

def cap_distance(distance, id):
    curdistance = _get_walk_distance(id)
    return (300-curdistance if distance>0 else curdistance*-1) if walk_will_max_distance(distance, id) else distance

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


def walk_is_maxed(id, max=300):
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
            cur.execute(
                """
                UPDATE users
                SET distance=0
                WHERE id NOT IN (
                    SELECT id FROM walks
                )
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


def update_team_total(teamid=None):
    print("Starting to update team totals")
    db = database.get_db()
    with db.cursor() as cur:
        if teamid is None:
            cur.execute(
                """
                UPDATE teams t
                SET distance=s.d
                FROM (
                    SELECT teamid, SUM(distance) d
                    FROM users
                    GROUP BY teamid
                ) s
                WHERE t.id=s.teamid
                """
            )
        else:
            cur.execute(
                """
                UPDATE teams t
                SET distance=s.d
                FROM (
                    SELECT teamid, SUM(distance) d
                    FROM users
                    GROUP BY teamid
                ) s
                WHERE t.id=s.teamid
                AND s.teamid=%s
                """,
                (teamid,)
            )
        cur.execute(
            """
            UPDATE teams
            SET distance=0
            WHERE id NOT IN (
                SELECT id FROM team_members
            )
            """
        )
    db.commit()
    print("Done updating team totals!")


def add_to_total(num, cur):
    cur.execute("UPDATE total SET distance=distance+%s", (num,))
    mqadd_update_leaderboard()


def add_to_team(num, teamid, cur):
    cur.execute(
        "UPDATE teams SET distance=distance+%s WHERE id=%s",
        (num, teamid)
    )


def fancy_float(n):
    try:
        n = float(n)
        if n % 1 == 0:
            return int(n)
        return n
    except ValueError:
        return 0

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

"""def remove_empty_teams():
    print("Removing empty teams...")
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            \"""
            DELETE FROM teams
            WHERE id NOT IN (
                SELECT id FROM team_members
            )
            \"""
        )
        print(f"Removed {cur.rowcount} empty teams.")
    db.commit()"""

def verify_walk_form(form, id):
    try:
        float(form.distance.data)
    except ValueError:
        return "Please submit a number."
    walkdistance = _get_walk_distance(id)
    if walkdistance>=300 and int(form.distance.data)>0:
        return "You can only go up to 300 km per day!"
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
            add_to_team(distancechange, getteamid(userid), cur)
            db.commit()
            update_total()

# Function needed for when current_user is out of context (such as webhook)
def connected_with_googlefit(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT googlefit FROM users WHERE id=%s;", (userid,))
        googlefit = cur.fetchone()[0]
    return googlefit

def autoload_day(userid, username, email, date, cur):
    print("Autoloading for " + username)
    if not haspayed(email) and not haspayed("all"):
        print("Isn't eligible (not in payed table)")
        return
    distance = get_day_distance(userid, date, cur)
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
            add_to_team(distance-float(walk[0]), getteamid(userid), cur)
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
        add_to_team(distance, getteamid(userid), cur)

# Since the walk API may have restrictive rates (such as Strava), not all of the users
# can be loaded at one time.
# TODO: come up with a way to only autoload users once/twice a day without webhooks, and do it so that only 25 users are loaded per 15 minutes
def autoload_day_all(date): # Autoload all users with Strava connected
    db = database.get_db()
    print("Autoloading all")
    with db.cursor() as cur:
        cur.execute("SELECT id, username, email FROM users WHERE googlefit=True ORDER BY id;")
        users = cur.fetchall()
        for userid, username, email in users:
            try:
                autoload_day(userid, username, email, date, cur)
                print("ok")
            except:
                print("Something went wrong. Possibly revoked access token.")
    db.commit()
    print("Done autoloading all")

def multiply_by_factor(date=date.today()):
    multiplier = get_multipliers(date)
    if multiplier:
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE walks SET distance=distance*%s WHERE walkdate=%s;",
                (multiplier["factor"], date)
            )
        db.commit()

def generate_team_name(cur):
    loopcount = 0
    while True: # Loop until we find a name that's not in use
        pendingchoice = random.choice(adjectives.adjectives) + " " + random.choice(nouns.nouns)
        cur.execute(
            "SELECT teamname FROM teams WHERE teamname=%s LIMIT 1",
            (pendingchoice,)
        )
        if cur.fetchone() == None:
            return pendingchoice
        print(f"WARNING: Skipping {pendingchoice} as a team name, since it's in use.")
        loopcount += 1
        if loopcount > 26:
            raise Exception("Couldn't find a team name") # Return an error, to prevent holding the server up forever


def create_team(userid):
    if getteamname(userid) is not None:
        return # Prevent creating a team if the user is on a team
    db = database.get_db()
    with db.cursor() as cur:
        teamname = generate_team_name(cur)
        # Create the team
        cur.execute(
            "INSERT INTO teams (teamname) VALUES (%s)", (teamname,)
        )
        # Get the team id
        cur.execute(
            "SELECT id FROM teams WHERE teamname=%s LIMIT 1", (teamname,)
        )
        teamid = cur.fetchone()[0]
        # Add user into team
        cur.execute(
            "INSERT INTO team_members (id, memberid) VALUES (%s, %s)",
            (teamid, userid)
        )
        cur.execute(
            "UPDATE users SET teamid=%s WHERE id=%s",
            (teamid, userid)
        )
        # Initialize the team distance
        update_team_total(teamid=teamid)
    db.commit()


def delete_team(teamid):
    db = database.get_db()
    with db.cursor() as cur:
        # Remove team members
        cur.execute(
            "DELETE FROM team_members WHERE id=%s", (teamid,)
        )
        cur.execute(
            "UPDATE users SET teamid=NULL where teamid=%s", (teamid,)
        )
        # Remove team
        cur.execute(
            "DELETE FROM teams WHERE id=%s", (teamid,)
        )
    db.commit()


def getteamname(userid, joincode=False):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT teamid FROM users WHERE id=%s LIMIT 1",
            (userid,)
        )
        teamid = cur.fetchone()
        if teamid is None:
            return None
        teamid = teamid[0]
        cur.execute(
            "SELECT teamname, distance, joincode FROM teams WHERE id=%s LIMIT 1",
            (teamid,)
        )
        res = cur.fetchone()
        return ((res[0], round(float(res[1]), 1)) if not joincode else (res[:3])) if res is not None else None


def getteamid(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT teamid FROM users WHERE id=%s LIMIT 1",
            (userid,)
        )
        teamid = cur.fetchone()
        if teamid is None:
            return None
        return teamid[0]


def getteamname_from_id(teamid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT teamname, distance, joincode FROM teams WHERE id=%s LIMIT 1",
            (teamid,)
        )
        res = cur.fetchone()
        return (res[0], round(float(res[1]), 1), res[2]) if res is not None else None


def join_team(userid, joincode=None):
    # If joincode is None, we need to leave the team we're on, otherwise, join the team
    # Check that we're on a team/not on a team
    teamname = getteamname(userid)
    if (teamname is None) == (joincode is None):
        return False
    db = database.get_db()

    with db.cursor() as cur:
        if joincode is None: # If we're leaving a team
            # Remove user from member table
            cur.execute(
                "DELETE FROM team_members WHERE memberid=%s", (userid,)
            )
            # Get user's teamid
            teamid = getteamid(userid)
            # Set user's teamid to NULL
            cur.execute(
                "UPDATE users SET teamid=NULL where id=%s", (userid,)
            )
        else: # If we're joining a team
            # Get team id of joincode
            cur.execute(
                "SELECT id FROM teams WHERE joincode=%s LIMIT 1", (joincode,)
            )
            teamid = cur.fetchone()
            if teamid is None:
                return False # Fail if team doesn't exist
            teamid = teamid[0]
            # Add user to member table
            cur.execute(
                "INSERT INTO team_members (id, memberid) VALUES (%s, %s)",
                (teamid, userid)
            )
            # Set user's teamid
            cur.execute(
                "UPDATE users SET teamid=%s WHERE id=%s",
                (teamid, userid)
            )
        # Either way, update team distance
        update_team_total(teamid=teamid)
    db.commit()
    return True
        

def new_join_code(teamid, remove=False):
    teamname = getteamname_from_id(teamid)
    if not teamname:
        return
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE teams SET joincode=%s WHERE id=%s",
            (
                (
                    "".join([
                        random.choice(
                        string.ascii_uppercase
                        + string.ascii_lowercase 
                        ) for i in range(5)
                    ]) + str(teamid)
                    if not remove else None
                ),
                teamid,
            )
        )
    db.commit()


def get_team_members(userid=None, teamid=None):
    db = database.get_db()
    with db.cursor() as cur:
        if userid:
            cur.execute(
                """
                SELECT t_m.memberid
                FROM users u
                INNER JOIN team_members t_m
                ON u.teamid=t_m.id
                WHERE u.id=%s
                """,
                (userid,)
            )
        elif teamid:
            cur.execute(
                "SELECT memberid FROM team_members WHERE id=%s", (teamid,)
            )
        else:
            return []
        members = cur.fetchall()
        # If no members in team, empty list is returned
        return [m[0] for m in members]


def get_team_member_names(userid=None, teamid=None):
    db = database.get_db()
    with db.cursor() as cur:
        if userid:
            cur.execute(
                """
                SELECT u.username, u.distance, u.wrdsbusername
                FROM users u
                INNER JOIN (
                    SELECT t_m.memberid mid
                    FROM users u
                    INNER JOIN team_members t_m
                    ON u.teamid=t_m.id
                    WHERE u.id=%s
                ) m
                ON u.id=m.mid
                """,
                (userid,)
            )
        elif teamid:
            cur.execute(
                """
                SELECT u.username, u.distance, u.wrdsbusername
                FROM users u
                INNER JOIN (
                    SELECT memberid mid FROM team_members WHERE id=%s
                ) m
                ON u.id=m.mid
                """,
                (teamid,)
            )
        else:
            return []
        res = cur.fetchall()
        # If no members in team, empty list is returned
        return [[i[0], fancy_float(i[1]), i[2]] for i in res]


# Various messages functions regarding redis message queue

# Webhook request from walkapi for creating walk
def mqadd_walkapi_create(userid, username, email):
    r = database.get_redis()
    message = {
        "type": "walkapi", # Type of message being sent (determines handler of message)
        "op": "create", # Kind of operation being performed
        "userid": userid,
        "username": username,
        "email": email,
        "date": date.today().isoformat()
    }
    r.rpush("messagequeue", json.dumps(message))

# Process a singular walkapi message from redis message queue, returns whether processing was successful (limit wasn't hit)
def mqprocess_walkapi(message, cur): # message should be dictionary
    r = database.get_redis()
    # Subject to walkapi rate limit (currently Strava: 100 req / 15 minutes)
    #TODO: change the rate limit IF the walk api changes
    WALKAPI_RATE_LIMIT = 100
    WALKAPI_LIMIT_TIME = 15*60 # In seconds
    # Check if redis walkapi queue has more than 100 elements in past 15 minutes
    if (r.llen("walkapi_ratelim_queue") > 0):
        tm = int(r.lindex("walkapi_ratelim_queue", 0))
    else:
        tm = -1
    while (tm > 0 and tm < int(time.time())-WALKAPI_LIMIT_TIME):
        r.lpop("walkapi_ratelim_queue")
        if (r.llen("walkapi_ratelim_queue") > 0):
            tm = int(r.lindex("walkapi_ratelim_queue", 0))
        else:
            tm = -1
    
    if r.llen("walkapi_ratelim_queue") >= WALKAPI_RATE_LIMIT:
        print("\nRATE LIMIT HIT\n")
        return False
        
    if message["op"] == "create":
        autoload_day(message["userid"], message["username"], message["email"], date.fromisoformat(message["date"]), cur)
        r.rpush("walkapi_ratelim_queue", int(time.time()))
        return True
    
    return False

# Update leaderboard message due to changes in distance
def mqadd_update_leaderboard():
    r = database.get_redis()
    message = {
        "type": "leaderboard",
        "op": "update"
    }
    r.rpush("messagequeue", json.dumps(message))
    r.set("update_leaderboard", "1") # Indicate leaderboard needs to be updated

def mqprocess_leaderboard(message):
    r = database.get_redis()

    # Leaderboard already updated
    if r.get("update_leaderboard") != "1":
        return True # Leaderboard messages don't need to be reprocessed
        
    if message["op"] == "update":
        update_leaderboard_positions()
        r.set("update_leaderboard", "0")
    
    return True

# Process items in messagequeue
def process_messagequeue():
    db = database.get_db()
    r = database.get_redis()
    with db.cursor() as cur:
        message = r.lmove("messagequeue", "unprocessedmessagequeue") # temporary storage of unprocessed messages
        while message:
            message = json.loads(message)
            if message["type"] == "walkapi":
                print("Message loaded: walkapi", message)
                processed = mqprocess_walkapi(message, cur)
            elif message["type"] == "leaderboard":
                print("Message loaded: leaderboard", message)
                processed = mqprocess_leaderboard(message)
            
            if processed:
                r.rpop("unprocessedmessagequeue")
            
            message = r.lmove("messagequeue", "unprocessedmessagequeue")
    db.commit()

    if r.llen("unprocessedmessagequeue") > 0:
        print(r.llen("unprocessedmessagequeue"), " unprocessed messages left")
        r.rename("unprocessedmessagequeue", "messagequeue")

def update_tick(context):
    with context:
        #update_leaderboard_positions()
        #autoload_day_all(date.today())
        process_messagequeue()

def long_update_tick(context):
    with context:
        multiply_by_factor(date.today()-timedelta(days=1))
        update_total()
        update_team_total()

def get_ui_settings(id=None):
    if id is None:
        id = "_"
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT userid, themeR, themeB, themeG, appname FROM ui_settings WHERE userid=%s OR userid='_'",
            (id,)
        )
        res = cur.fetchall()
    uiSettings = {}
    # A maximum of 2 results should be returned, one with _ and one with the user's id
    # We want to proccess defaults before any user-specific values, which we can ensure
    # by sorting the list, using a key that assigns "_" 0 and everything else 1
    res.sort(key=lambda a: 0 if a[0] == "_" else 1)
    for row in res:
        for settingName, settingValue in zip(["themeR", "themeB", "themeG", "appName"], row[1:]):
            if settingValue != None:
                uiSettings.update({settingName: settingValue})
            elif settingName not in uiSettings:
                uiSettings.update({settingName: None})
    return uiSettings

def get_big_image(id=None):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT userid, bigimage, bigimage_hash FROM ui_settings WHERE userid=%s OR userid='_'",
            (id,)
        )
        res = cur.fetchall()
    res.sort(key=lambda a: 0 if a[0] == "_" else 1)
    bigimage = b""
    bigimage_hash = b""
    for row in res:
        if row[1] != None:
            bigimage = row[1]
            bigimage_hash = row[2].hex()
    return bigimage, bigimage_hash