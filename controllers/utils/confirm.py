from flask import render_template, current_app as app
from itsdangerous import URLSafeTimedSerializer

from flask_mail import Message

from app import mail


def get_confirm_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt=app.config['SECURITY_PASSWORD_SALT'])
    return serializer.dumps(email)


def authenticate_confirm_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt=app.config['SECURITY_PASSWORD_SALT'])
    try:
        email = serializer.loads(token, max_age=1800)
    except:
        return False
    return email

def email_confirm_token(email, confirm_url):
    msg = Message(
        'Confirm WCI Walks account',
        recipients=(email,),
        html = render_template('email.html', confirm_url=confirm_url),
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)