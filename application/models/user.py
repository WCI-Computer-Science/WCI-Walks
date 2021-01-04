import sys, json
from flask import current_app, redirect, url_for
import flask_login
from . import database, loginmanager
from datetime import date, timedelta
from application.templates.utils import isadmin

login_manager = loginmanager.get_login_manager()

class User:
    def __init__(self, userid=None, email=None, username=None, distance=0, authenticated=1, active=1):
        self.id = userid
        self.email = email
        self.username = username
        self.wrdsbusername = email.split("@")[0] if email != None else None
        self.distance = distance
        self.is_authenticated = authenticated
        self.is_active = active
        self.is_anonymous = False

    def add_distance(self, distance):
        self.distance = round(self.distance + distance, 1)

    def write_db(self, cur):
        cur.execute(
            'INSERT INTO users (id, email, username, wrdsbusername, distance, active) VALUES (%s, %s, %s, %s, %s, %s);',
            (self.id, self.email, self.username, self.wrdsbusername, self.distance, self.is_active)
        )

    def update_distance_db(self, cur):
        cur.execute(
            'UPDATE users SET distance=%s WHERE id=%s;', (self.distance, self.id)
        )

    def read_db(self, cur):
        cur.execute(
            'SELECT * FROM users WHERE id=%s LIMIT 1;', (self.id,)
        )
        user = cur.fetchone()
        self.email = user['email']
        self.username = user['username']
        self.distance = user['distance']
        self.is_active = user['active']

    def get_walk(self, date, cur):
        cur.execute(
            'SELECT * FROM walks WHERE id=%s AND walkdate=%s LIMIT 1', (self.id, date)
        )
        return cur.fetchone()

    def insert_walk(self, distance, date, cur):
        cur.execute(
            'INSERT INTO walks (id, username, distance, walkdate) VALUES (%s, %s, %s, %s);',
            (self.id, self.username, distance, date)
        )

    def update_walk(self, distance, date, walk, cur):
        cur.execute(
            'UPDATE walks SET distance=%s WHERE id=%s AND walkdate=%s;',
            (round(walk['distance'] + distance, 1), self.id, date)
        )

    def get_walk_chart_data(self, cur, id=None):
        if id is None: useid = self.id
        else: useid = id
        cur.execute(
            'SELECT walkdate, distance FROM walks WHERE id=%s;', (useid,)
        )
        allwalks = cur.fetchall()
        allwalks.sort(key=lambda row: row['walkdate'])

        walks = {}
        if len(allwalks) > 0:
            for i in range((allwalks[-1][0] - allwalks[0][0]).days + 1):
                walks[allwalks[0][0] + timedelta(days=i)] = 0
            for walkdate, walkdistance in allwalks:
                walks[walkdate] = walkdistance

        return list(walks.keys()), list(walks.values())

    def get_id(self):
        return self.id

    def is_admin(self):
        return isadmin(self.id)

    # Static methods
    @staticmethod
    def exists(userid, cur):
        cur.execute(
            'SELECT id FROM users WHERE id=%s LIMIT 1;', (userid,)
        )
        return cur.fetchone()

@login_manager.user_loader
def load_user(userid):
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM users WHERE id=%s;', (userid,)
        )
        user = cur.fetchone()

    if not user:
        return None

    return User(
        user['id'],
        user['email'],
        user['username'],
        user['distance'],
        user['active']
    )
