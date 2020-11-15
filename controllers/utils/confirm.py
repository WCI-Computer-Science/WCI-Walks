from flask import current_app as app
from itsdangerous import URLSafeTimedSerializer


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