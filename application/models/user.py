from datetime import timedelta

from application.models.utils import (
    get_credentials_from_wrdsbusername,
    get_team_members,
    get_wrdsbusername_from_id,
    getteamname,
    getteamid,
    isadmin,
)

from . import database, loginmanager

login_manager = loginmanager.get_login_manager()


class User:
    def __init__(
        self,
        userid=None,
        email=None,
        username=None,
        distance=0,
        authenticated=1,
        active=1,
    ):
        self.id = userid
        self.email = email
        self.username = username
        self.wrdsbusername = email.split("@")[0] if email is not None else None
        self.distance = distance
        self.is_authenticated = authenticated
        self.is_active = active
        self.is_anonymous = False
        self.liked = None
    
    def add_refresh(self, refresh, cur):
        cur.execute(
            "UPDATE users SET refreshtoken=%s WHERE id=%s;",
            (refresh, self.id)
        )

    def get_liked(self):
        db = database.get_db()
        with db.cursor() as cur:
            if self.liked==None:
                cur.execute(
                    "SELECT liked FROM users WHERE id=%s;", (self.id,)
                )
                liked = cur.fetchone()[0]
                self.liked = liked.split(",") if liked != None else []
        return self.liked

    def like(self, to):
        db = database.get_db()
        with db.cursor() as cur:
            if to not in self.get_liked():
                cur.execute(
                    "UPDATE users SET likes=Coalesce(likes, 0)+1, likediff=Coalesce(likediff, 0)+1 WHERE id=%s;", (to,)
                )
                self.liked.append(to)
                cur.execute(
                    "UPDATE users SET liked=%s WHERE id=%s;", (",".join(self.liked), self.id)
                )
                db.commit()

    def unlike(self, to):
        db = database.get_db()
        with db.cursor() as cur:
            if to in self.get_liked():
                cur.execute(
                    "UPDATE users SET likes=Coalesce(likes, 0)-1, likediff=Coalesce(likediff, 0)-1 WHERE id=%s;", (to,)
                )
                self.liked.remove(to)
                cur.execute(
                    "UPDATE users SET liked=%s WHERE id=%s;", (",".join(self.liked), self.id)
                )
                db.commit()

    def get_likes(self):
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT likes FROM users WHERE id=%s;", (self.id,)
            )
            likes = cur.fetchone()[0]
            return int(likes) if likes != None else 0

    def get_new_likes(self, clear=False):
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT likediff FROM users WHERE id=%s;", (self.id,)
            )
            likediff = cur.fetchone()[0]
            if clear:
                cur.execute(
                    "UPDATE users SET likediff=0 WHERE id=%s;", (self.id,)
                )
                db.commit()
            return int(likediff) if likediff!= None else 0

    def get_leaderboard_position(self):
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT position FROM users WHERE id=%s;", (self.id,)
            )
            return cur.fetchone()[0]

    def add_distance(self, distance):
        self.distance = round(float(self.distance) + distance, 1)

    def write_db(self, cur):
        cur.execute(
            """
                INSERT INTO users
                (id, email, username, wrdsbusername, distance, active)
                VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                self.id,
                self.email,
                self.username,
                self.wrdsbusername,
                self.distance,
                self.is_active,
            )
        )

    def update_distance_db(self, cur):
        cur.execute(
            "UPDATE users SET distance=%s WHERE id=%s;",
            (self.distance, self.id)
        )

    def read_db(self, cur):
        cur.execute("SELECT * FROM users WHERE id=%s LIMIT 1;", (self.id,))
        user = cur.fetchone()
        self.email = user["email"]
        self.username = user["username"]
        self.distance = user["distance"]
        self.is_active = user["active"]

    def get_walk(self, date, cur, id=None):
        if id is not None:
            useid = id
        else:
            useid = self.id
        cur.execute(
            "SELECT * FROM walks WHERE id=%s AND walkdate=%s LIMIT 1;",
            (useid, date)
        )
        return cur.fetchone()

    def insert_walk(self, distance, date, cur, id=None):
        if id is not None:
            useid = id
        else:
            useid = self.id
        username = get_credentials_from_wrdsbusername(
            get_wrdsbusername_from_id(useid)
        )[1]
        cur.execute(
            """
                INSERT INTO walks
                (id, username, distance, walkdate)
                VALUES (%s, %s, %s, %s);
            """,
            (useid, username, distance, date)
        )

    def set_ui_settings(self, settings, cur, globally):
        if globally:
            useid = "_"
        else:
            useid = self.id
        for settingName in settings:
            if settingName not in ["themeR", "themeB", "themeG", "bigimage", "bigimage_hash", "favicon", "favicon_hash"]:
                print("Setting name not in allowed list (themeR, themeB, themeG, bigimage, bigimage_hash, favicon and favicon_hash), skipping")
                continue
            cur.execute(
                "UPDATE ui_settings SET " + settingName + "=%s WHERE userid=%s",
                (settings[settingName], useid,)
            )

    def update_walk(self, distance, date, walk, cur, replace=False, id=None):
        if id is not None:
            useid = id
        else:
            useid = self.id
        if self.get_walk(date, cur, id=useid) is not None:
            cur.execute(
                "UPDATE walks SET distance=%s WHERE id=%s AND walkdate=%s;",
                (
                    round(
                        (distance if replace else float(walk["distance"]) + distance),
                        1
                    ),
                    useid,
                    date,
                )
            )
        else:
            self.insert_walk(distance, date, cur, id=useid)

    def get_walk_chart_data(self, cur, id=None):
        if id is None:
            useid = self.id
        else:
            useid = id
        cur.execute(
            "SELECT walkdate, distance FROM walks WHERE id=%s;", (useid,)
        )
        allwalks = cur.fetchall()
        allwalks.sort(key=lambda row: row["walkdate"])

        walks = {}
        if len(allwalks) > 0:
            for i in range((allwalks[-1][0] - allwalks[0][0]).days + 1):
                walks[allwalks[0][0] + timedelta(days=i)] = 0
            for walkdate, walkdistance in allwalks:
                walks[walkdate] = walkdistance

        return list(walks.keys()), list(walks.values())
    
    def toggle_googlefit(self, userid, cur, val=None):
        if val is None:
            cur.execute("UPDATE users SET googlefit = NOT googlefit WHERE id=%s;", (userid,))
        else:
            cur.execute("UPDATE users SET googlefit=%s WHERE id=%s;", (val, userid))
    
    def connected_with_googlefit(self):
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute("SELECT googlefit FROM users WHERE id=%s;", (self.id,))
            googlefit = cur.fetchone()[0]
        return googlefit

    def get_id(self):
        return self.id

    def is_admin(self):
        return isadmin(self.id)

    def team_name(self, joincode=False):
        return getteamname(self.id, joincode=joincode)
    
    def team_id(self):
        return getteamid(self.id)

    def alone_on_team(self):
        res = get_team_members(userid=self.id)
        # Return true if user's team is empty (which shouldn't happen)
        return len(res) <= 1

    # Static methods
    @staticmethod
    def exists(userid, cur):
        cur.execute("SELECT id FROM users WHERE id=%s LIMIT 1;", (userid,))
        return cur.fetchone()

@login_manager.user_loader
def load_user(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id=%s;", (userid,))
        user = cur.fetchone()

    if not user:
        return None

    return User(
        user["id"],
        user["email"],
        user["username"],
        user["distance"],
        user["active"]
    )
