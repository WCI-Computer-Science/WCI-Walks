import sys
from flask import current_app, redirect, url_for
import flask_login
from . import database, loginmanager

login_manager = loginmanager.get_login_manager()

class User:
    def __init__(self, userid=None, email=None, username=None, distance=0, authenticated=1, active=1):
        self.id = userid
        self.email = email
        self.username = username
        self.distance = distance
        self.is_authenticated = authenticated
        self.is_active = active
        self.is_anonymous = False
    
    def add_distance(self, distance):
        self.distance = round(self.distance + distance, 1)
    
    def write_db(self):
        database.get_db().execute(
            'INSERT INTO users (id, email, username, distance, active) VALUES (?, ?, ?, ?, ?)',
            (self.id, self.email, self.username, self.distance, self.is_active)
        )
    
    def update_distance_db(self):
        database.get_db().execute(
            'UPDATE users SET distance=? WHERE id=?', (self.distance, self.id)
        )

    def read_db(self):
        user = database.get_db().execute(
            'SELECT id FROM users WHERE id=? LIMIT 1', (self.id,)
        ).fetchone()
        self.email = user['email']
        self.username = user['username']
        self.distance = user['distance']
        self.is_active = user['active']
    
    def get_walk(self, date):
        return database.get_db().execute(
            'SELECT * FROM walks WHERE id=? AND walkdate=?', (self.id, date)
        ).fetchone()
    
    def insert_walk(self, distance, date):
        database.get_db().execute(
            'INSERT INTO walks (id, username, distance, walkdate) VALUES (?, ?, ?, ?)',
            (self.id, self.username, distance, date)
        )
    
    def update_walk(self, distance, date, walk):
        database.get_db().execute(
            'UPDATE walks SET distance=? WHERE id=? AND walkdate=?',
            (round(walk['distance'] + distance, 1), self.id, date)
        )
            
    def get_id(self):
        return self.id
    
    # Static methods
    @staticmethod
    def exists(userid):
        db = database.get_db()
        return db.execute(
            'SELECT id FROM users WHERE id=? LIMIT 1', (userid,)
        ).fetchone()

@login_manager.user_loader
def load_user(userid):
    db = database.get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id=?', (userid,)
    ).fetchone()

    if not user:
        return None

    return User(
        user['id'],
        user['email'],
        user['username'],
        user['distance'],
        user['active']
    )