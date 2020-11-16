import functools, sys, datetime, json

from flask import abort, Blueprint, current_app, url_for, redirect, render_template, request, requests, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer

from wtforms import Form, PasswordField, DecimalField, StringField, SubmitField, validators
from wtforms.fields.html5 import EmailField, IntegerField

from models import *

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
@login_required
def info():
    if 'userid' not in session:
        return redirect(url_for('userinfo.login'))
    
    db = database.get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id=?', (session['userid'],)
    ).fetchone()

    if not user['confirmed']:
        # Tell user to authenticate email
        return render_template()

    form = SubmitDistanceForm(request.form)
    message = None

    if request.method == 'GET':
        return render_template('users.html', form=form)

    date = str(datetime.date.today())
    error = None
    if form.validate():
        distance = float(form.distance.data)
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
            elif not user['confirmed']:
                error = 'This account hasn\'t been confirmed. Check your email or sign up again.'
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

@bp.route('/authorize', methods=('GET', 'POST'))
def authorize():
    auth_endpoint = oauth.get_google_configs()['authorization_endpoint']

    request_uri = oauth.get_client().prepare_request_uri(
        auth_endpoint,
        redirect_uri=request.base_url + '/confirmlogin',
        scope=['openid', 'email', 'profile']
    )
    return redirect(request_uri)

@bp.route('/confirmlogin', methods=('GET', 'POST'))
def confirmlogin():
    code = request.args.get('code')
    client = oauth.get_client()
    token_url, headers, body = client.prepare_token_request(
        oauth.get_google_configs()['token_endpoint'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    uri, headers, body = client.add_token(oauth.get_google_configs()["userinfo_endpoint"])
    userinfo_response = requests.get(uri, headers=headers, data=body).json()
    if userinfo_response.get("email_verified"):
        userid = userinfo_response["sub"]
        email = userinfo_response["email"]
        username = userinfo_response["name"]
    else:
        return "Email unavailable or not unverified.", 400
    
    if not user.User.exists(userid):
        current_user = user.User(userid=userid, email=email, username=username)
        current_user.write_db()
    else:
        current_user = user.User(userid=userid)
        current_user.read_db()
    
    login_user(current_user)
    return redirect(url_for('userinfo.info'))

@bp.route('/logout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.home'))
