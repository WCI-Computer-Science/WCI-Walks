import flask_login
import models.database

class User:
    def __init__(self, email, username=None, authenticated=False, active=True):
        self.email = email
        self.username = username
        self.distance = 0
        self.authenticated = authenticated
        self.active = active
    
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        try:
            return self.id 
        except:
            db = database.get_db()
            self.id = str(db.execute(
                'SELECT id FROM users WHERE email=?', (self.email,)
            )[0])
            return self.id

@login_manager.user_loader
def load_user(userid):
    db = database.get_db()
    return db.execute(
        'SELECT * FROM users WHERE id=?', (userid,)
    ).fetchone()