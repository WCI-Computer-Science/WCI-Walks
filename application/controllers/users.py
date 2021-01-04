import functools, sys, datetime, json, time

from flask import abort, Blueprint, current_app, url_for, flash, redirect, render_template, request, session
from flask_login import current_user, login_user, logout_user, login_required

from wtforms import Form, PasswordField, DecimalField, StringField, SubmitField, validators
from wtforms.fields.html5 import EmailField, IntegerField

from application.models import *
from application.templates.utils import get_credentials_from_wrdsbusername, walk_will_max_distance, walk_is_maxed, is_blocked, add_to_total

bp = Blueprint('users', __name__, url_prefix='/users')

class SubmitDistanceForm(Form):
    distance = DecimalField(
        "Log your walk distance (in km)",
        places=2
    )
    submit = SubmitField()

@bp.route('/', methods=('GET', 'POST'))
@login_required
def info():
    db = database.get_db()
    date = datetime.date.today()
    form = SubmitDistanceForm(request.form)

    if request.method == 'POST':
        form.distance.validators = [
            validators.InputRequired(),
            validators.NumberRange(min=0.01, max=42, message="Invalid distance"),
            walk_is_maxed(current_user.get_id(), max=42),
        ]
        if form.validate():
            with db.cursor() as cur:
                while is_blocked():
                    time.sleep(100)
                walk = current_user.get_walk(date, cur)
                walkwillmaxdistance = walk_will_max_distance(float(form.distance.data), current_user.get_id())
                distance = round((float(form.distance.data) if not(walkwillmaxdistance) else 42-walk["distance"]), 1)
                total = database.get_total(cur)

                if walk is None:
                    current_user.insert_walk(distance, date, cur)
                else:
                    current_user.update_walk(distance, date, walk, cur)

                add_to_total(distance)

                current_user.add_distance(distance)
                current_user.update_distance_db(cur)

            db.commit()
            if walkwillmaxdistance:
                flash("Your walk was partly recorded. You can't go more than 42 km per day.")
            else:
                flash("You've successfully updated the distance!")
        else:
            flash("You can only go between 0 and 42 km per day!")
    
    with db.cursor() as cur:
        labels, data = current_user.get_walk_chart_data(cur)

    return render_template(
        'users.html',
        username=current_user.username,
        form=form,
        labels=labels,
        data=data
    )

@bp.route('/viewprofile/<username>', methods=('GET', 'POST'))
@login_required
def viewprofile(username):
    db = database.get_db()
    with db.cursor() as cur:
        userid, name = get_credentials_from_wrdsbusername(username, cur)
        labels, data = current_user.get_walk_chart_data(cur, id=userid)

    return render_template(
        'otherusers.html',
        labels=labels,
        data=data,
        name=name
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

    if idinfo.get("email_verified") and idinfo.get("hd") == "wrdsb.ca":
        userid = idinfo["sub"]
        email = idinfo["email"]
        username = idinfo["name"]
    else:
        flash("Email invalid. Are you using your WRDSB email?")
        return redirect(url_for('users.login'))
    
    print(idinfo, file=sys.stderr)
    
    db = database.get_db()
    with db.cursor() as cur:
        if not user.User.exists(userid, cur):
            current_user = user.User(userid=userid, email=email, username=username)
            current_user.write_db(cur)
            db.commit()
        else:
            current_user = user.User(userid=userid)
            current_user.read_db(cur)

    login_user(current_user)
    return redirect(url_for('users.info'))

@bp.route('/logout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@login_required
def logout():
    logout_user()
    # add a log out view in the future
    return redirect(url_for('index.home'))
