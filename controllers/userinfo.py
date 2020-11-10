import functools, sys #sys for debugging

from flask import Blueprint, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from models import database
from wtforms import Form, PasswordField, DecimalField, StringField, SubmitField, validators
from wtforms.fields.html5 import EmailField, IntegerField

bp = Blueprint('userinfo', __name__, url_prefix='/users')

class SubmitDistanceForm(Form):
    distance = DecimalField(
        "Log your distance:",
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

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def info():
    if 'userid' not in session:
        return redirect('/users/login')
    db = database.get_db()
    form = SubmitDistanceForm(request.form)
    return render_template('users.html', form=form)

@bp.route('/signup', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def signup():
    good=False # a variable instead of indenting everything even more
    userform = SignupForm(request.form)
    if request.method == 'POST':
        if userform.validate(): good=True
    if good:
        username = userform.username.data
        email = userform.email.data
        password = userform.password.data

        print(username, file=sys.stderr)

        error = None
        db = database.get_db()

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
            return redirect('/users/login')

        #in the future, alert front end of error with http response
        print(error, file=sys.stderr)
    return render_template('usersignup.html', userform=userform)

@bp.route('/login', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def login():
    good=False # a variable instead of indenting everything even more
    userform = LoginForm(request.form)
    if request.method == 'POST':
        if userform.validate():
            good=True
    if good:
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
            return redirect('/users')

        #in the future, alert front end of error with http response
        print(error, file=sys.stderr)

    return render_template('userlogin.html', userform=userform)

@bp.route('/logout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def logout():
    session.clear()
    return redirect('/')
