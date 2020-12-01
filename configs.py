import os
import secrets

SECRET_KEY = secrets.secret_key
DB = os.environ['DATABASE_URL']
GOOGLE_CLIENT_ID = secrets.google_client_id
GOOGLE_CLIENT_SECRET = secrets.google_client_secret
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
