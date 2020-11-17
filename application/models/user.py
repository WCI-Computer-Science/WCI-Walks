import sys
from flask import current_app, redirect, url_for
import flask_login
from . import database, loginmanager

login_manager = loginmanager.get_login_manager()

class User:
    def __init__(self, userid=None, email=None, username=None, distance=0, active=1):
        self.id = userid
        self.email = email
        self.username = username
        self.distance = distance
        self.active = active
    
    def add_distance(self, distance):
        self.distance += distance
    
    def write_db(self):
        db = database.get_db()
        db.execute(
            'REPLACE INTO users (id, email, username, distance, active) VALUES (?, ?, ?, ?, ?)',
            (self.id, self.email, self.username, self.distance, self.active)
        )
    
    def read_db(self):
        db = database.get_db()
        user = db.execute(
            'SELECT id FROM users WHERE id=? LIMIT 1', (self.id,)
        ).fetchone()
        self.email = user['email']
        self.username = user['username']
        self.distance = user['distance']
        self.active = user['active']
        
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
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