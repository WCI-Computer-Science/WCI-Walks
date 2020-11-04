import functools, sys

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from models import database

bp = Blueprint('login', __name__, url_prefix='/users')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp.route('/login', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def login():
    if request.method == 'POST':
        print('Ok2', file=sys.stderr)       
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        error = None
        db = database.get_db()

        if not username or not email or not password:
            error = "Please fill out all values."
        if db.execute(
            "SELECT id FROM users WHERE email=?", (email,)
        ).fetchone() is None:
            error = "We couldn't find your account.\n\
            Please sign up if you haven't already."
        
        if error is None:
            #store a cookie
            print('Store a cookie', file=sys.stderr)

        flash(error) #in the future, alert front end (maybe make an error html file?)

    return render_template('users.html')

@bp.route('/sign-up', methods=('GET', 'POST'))
def signup():
    return render_template('users.html') #fix later