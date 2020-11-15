import functools, sys, datetime #sys for debugging

from flask import Blueprint, url_for, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from models import database
from wtforms import Form, PasswordField, DecimalField, StringField, SubmitField, validators
from wtforms.fields.html5 import EmailField, IntegerField

bp = Blueprint('userinfo', __name__, url_prefix='/users')

class SubmitDistanceForm(Form):
    distance = DecimalField(
        "Log your distance",
        [validators.InputRequired(), validators.NumberRange(min=0.01, max=42, message="Invalid distance")],
        places=2)
    submit = SubmitField()

class SignupForm(Form):
    username = StringField("First and last name", [validators.InputRequired()])
    email = EmailField("WRDSB email address", [validators.InputRequired(), validators.Email()])
    password = PasswordField("Password", [validators.InputRequired()])
    confirmpassword = PasswordField("Confirm password",
        [validators.InputRequired(), validators.EqualTo('password', message='Passwords must match')])
    submit = SubmitField()

class LoginForm(Form):
    email = EmailField("Email address", [validators.InputRequired(), validators.Email()])
    password = PasswordField("Password", [validators.InputRequired()])
    submit = SubmitField()

@bp.route('/', methods=('GET', 'POST'))
def info():
    if 'userid' not in session:
        return redirect(url_for('userinfo.login'))

    form = SubmitDistanceForm(request.form)
    message = None

    if request.method == 'GET':
        return render_template('users.html', form=form)

    db = database.get_db()
    date = str(datetime.date.today())
    error = None
    if form.validate():
        distance = float(form.distance.data)
        user = db.execute(
            'SELECT * FROM users WHERE id=?', (session['userid'],)
        ).fetchone()
        walk = db.execute(
            'SELECT * FROM walks WHERE id=? AND walkdate=?', (session['userid'], date)
        ).fetchone()
        total = db.execute(
            'SELECT * FROM total'
        ).fetchone()
        
        if walk is None:
            db.execute(
                'INSERT INTO walks (id, username, distance, walkdate) VALUES (?, ?, ?, ?)',
                (session['userid'], user['username'], distance, date)
            )
        else:
            db.execute(
                'UPDATE walks SET distance=? WHERE id=? AND walkdate=?',
                (round(walk['distance'] + distance, 1), session['userid'], date)
            )
        
        if total is None:
            db.execute(
                'INSERT INTO total (distance) VALUES (?)', (distance,)
            )
        else:
            db.execute(
                'UPDATE total SET distance=?', (round(total['distance'] + distance, 1),)
            )
        
        db.execute(
            'UPDATE users SET distance=? WHERE id=?', (round(user['distance'] + distance, 1), session['userid'])
        )

        db.commit()
        message = "You've successfully updated the distance!"
    else:
        error = "Please enter a number between 0 and 42."

    return render_template('users.html', form=form, error=error, message=message)

@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    userform = SignupForm(request.form)

    if request.method == 'GET':
        return render_template('usersignup.html', userform=userform)

    if userform.validate():
        username = userform.username.data
        email = userform.email.data
        password = userform.password.data

        print(username, file=sys.stderr)

        error = None
        db = database.get_db()
        if email[-9:] != "@wrdsb.ca":
            error = "Please use a WRDSB email!"
        if not username or not email or not password:
            error = 'Please fill out all values.'
        elif db.execute(
                'SELECT id FROM users WHERE email=?', (email,)
             ).fetchone() is not None:
                error = 'This email is already taken.'

        if error is None:
            # implement two factor auth
            db.execute(
                'INSERT INTO users (email, username, password, distance) VALUES (?, ?, ?, 0)',
                (email, username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('userinfo.login'))

        #in the future, alert front end of error with http response
        print(error, file=sys.stderr)
    else:
        error="Please check that all fields are filled out correctly!"
    return render_template('usersignup.html', userform=userform, error=error)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    userform = LoginForm(request.form)

    if request.method == 'GET':
        return render_template('userlogin.html', userform=userform)

    if userform.validate():
        email = userform.email.data
        password = userform.password.data

        print(email, file=sys.stderr)

        error = None
        db = database.get_db()

        if not email or not password:
            error = 'Please fill out all values.'
        else:
            user = db.execute(
                'SELECT * FROM users WHERE email=?', (email,)
            ).fetchone()
            if user is None or not check_password_hash(user['password'], password):
                error = 'Login credentials failed. Have you signed up yet?'
            else:
                print(user["username"], file=sys.stderr)
        if error is None:
            session.clear()
            session['userid'] = user['id']
            session['email'] = user['email']
            print('Store a cookie', file=sys.stderr)
            return redirect(url_for('userinfo.info'))

        #in the future, alert front end of error with http response
        print(error, file=sys.stderr)
    else:
        error="Please check that you have filled out all fields correctly!"
    return render_template('userlogin.html', userform=userform, error=error)

@bp.route('/logout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def logout():
    session.clear()
    return redirect(url_for('index.home'))
