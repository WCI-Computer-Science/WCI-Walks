import os

import secrets

ENV = 'development'
SECRET_KEY = secrets.secret_key
SECURITY_PASSWORD_SALT = secrets.security_password_salt
DB = os.environ['DATABASE_URL']
GOOGLE_CLIENT_ID = secrets.google_client_id
GOOGLE_CLIENT_SECRET = secrets.google_client_secret
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"