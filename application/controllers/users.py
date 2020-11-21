import functools, sys, datetime, json

from flask import abort, Blueprint, current_app, url_for, flash, redirect, render_template, request, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer

from wtforms import Form, PasswordField, DecimalField, StringField, SubmitField, validators
from wtforms.fields.html5 import EmailField, IntegerField

from application.models import *

bp = Blueprint('users', __name__, url_prefix='/users')

class SubmitDistanceForm(Form):
    distance = DecimalField(
        "Log your distance",
        [validators.InputRequired(), validators.NumberRange(min=0.01, max=42, message="Invalid distance")],
        places=2)
    submit = SubmitField()

@bp.route('/', methods=('GET', 'POST'))
@login_required
def info():
    form = SubmitDistanceForm(request.form)

    if request.method == 'GET':
        return render_template(
            'users.html',
            username=current_user.username,
            form=form
        )

    db = database.get_db()
    date = str(datetime.date.today())
    if form.validate():
        distance = float(form.distance.data)
        walk = current_user.get_walk(date)
        total = db.execute(
            'SELECT * FROM total'
        ).fetchone()
        
        if walk is None:
            current_user.insert_walk(distance, date)
        else:
            current_user.update_walk(distance, date, walk)
        
        if total is None:
            db.execute(
                'INSERT INTO total (distance) VALUES (?)', (distance,)
            )
        else:
            db.execute(
                'UPDATE total SET distance=?', (round(total['distance'] + distance, 1),)
            )
        
        current_user.add_distance(distance)
        current_user.update_distance_db()

        db.commit()
        flash("You've successfully updated the distance!")
    else:
        flash("Please enter a number between 0 and 42.")

    return render_template(
        'users.html',
        username=current_user.username,
        form=form,
    )

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.info'))
    
    return render_template('userlogin.html')

@bp.route('/authorize', methods=('GET', 'POST'))
def authorize():
    if current_user.is_authenticated:
        return redirect(url_for('users.info'))
    
    auth_endpoint = oauth.get_google_configs()['authorization_endpoint']

    request_uri = oauth.get_client().prepare_request_uri(
        auth_endpoint,
        redirect_uri=request.base_url + '/confirmlogin',
        scope=['openid', 'email', 'profile']
    )
    return redirect(request_uri)

@bp.route('/authorize/confirmlogin', methods=('GET', 'POST'))
def confirmlogin():
    code = request.args.get('code')
    id_token = oauth.get_id_token(code)
    idinfo = oauth.verify_id_token(id_token)


    if idinfo.get("email_verified") and idinfo.get("hd"):
        userid = idinfo["sub"]
        email = idinfo["email"]
        username = idinfo["name"]
    else:
        flash("Email invalid. Are you using your WRDSB email?")
        return redirect(url_for('users.login'))
    
    print(idinfo, file=sys.stderr)
    
    if not user.User.exists(userid):
        current_user = user.User(userid=userid, email=email, username=username)
        current_user.write_db()
        database.get_db().commit()
    else:
        current_user = user.User(userid=userid)
        current_user.read_db()

    login_user(current_user)
    return redirect(url_for('users.info'))

@bp.route('/logout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@login_required
def logout():
    logout_user()
    # add a log out view in the future
    return redirect(url_for('index.home'))
