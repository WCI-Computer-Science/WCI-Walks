from flask import current_app, g
from flask_login import LoginManager

def init_login_manager():
    login_manager = LoginManager()
    login_manager.init_app(current_app)
    login_manager.login_view = 'users.login'
    login_manager.login_message = 'Please log in first.'
    return login_manager

def get_login_manager():
    if 'login_manager' not in g:
        g.login_manager = init_login_manager()
    return g.login_manager