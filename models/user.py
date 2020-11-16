from flask import redirect, url_for
import flask_login
import models.database

class User:
    def __init__(self, userid=None, email=None, username=None, distance=0, authenticated=0, active=1):
        self.id = userid
        self.email = email
        self.username = username
        self.distance = distance
        self.authenticated = authenticated
        self.active = active
    
    def add_distance(self, distance):
        self.distance += distance
        
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        if self.id is not None:
            return self.id 
        else:
            db = database.get_db()
            self.id = str(db.execute(
                'SELECT id FROM users WHERE email=?', (self.email,)
            )[0])
            return self.id

@login_manager.user_loader
def load_user(userid):
    db = database.get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id=?', (userid,)
    ).fetchone()
    return User(
        user['id'],
        user['email'],
        user['username'],
        user['distance'],
        user['authenticated'],
        user['active']
    )

@login_manager.unauthorized
def unauthorized():
    redirect(url_for('userinfo.login'))