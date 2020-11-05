import functools, sys

from flask import Blueprint, redirect, render_template, request
from models import database

bp = Blueprint('login', __name__, url_prefix='/users')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def info():
    return render_template('users.html') #fix later


@bp.route('/login', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def login():
    if request.method == 'POST':      
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        print(username, file=sys.stderr)

        error = None
        db = database.get_db()

        if not username or not email or not password:
            error = "Please fill out all values."
        else:
            user = db.execute(
                "SELECT id FROM users WHERE email=?", (email,)
            ).fetchone()
            if user is None:
                error = 'Username not found. Have you signed up yet?'
            elif password != user['password']:
                error = 'Incorrect password.'
        
        if error is None:
            #store a cookie
            print('Store a cookie', file=sys.stderr)

        #in the future, alert front end with http response

    return render_template('users.html')

@bp.route('/sign-up', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def signup():
    return render_template('users.html') #fix later