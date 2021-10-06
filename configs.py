import os
from datetime import datetime
try:
    import secrets

    SECRET_KEY = secrets.secret_key
    GOOGLE_CLIENT_ID = secrets.google_client_id
    GOOGLE_CLIENT_SECRET = secrets.google_client_secret
    WALKAPI_CLIENT_ID = secrets.walkapi_client_id
    WALKAPI_CLIENT_SECRET = secrets.walkapi_client_secret
except (ModuleNotFoundError, AttributeError):
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
        GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
        WALKAPI_CLIENT_ID = os.environ["WALKAPI_CLIENT_ID"]
        WALKAPI_CLIENT_SECRET = os.environ["WALKAPI_CLIENT_SECRET"]
    except KeyError:  # Probably running on travis, no need for real values here, but warn anyways
        print("Warn: Could not load secrets, using bogus values.")
        SECRET_KEY = ""
        GOOGLE_CLIENT_ID = ""
        GOOGLE_CLIENT_SECRET = ""
        WALKAPI_CLIENT_ID = ""
        WALKAPI_CLIENT_SECRET = ""
        
try:
    import secrets

    DB = os.environ["DATABASE_URL"]
    DONT_LOAD_DB = False
except KeyError:
    try:
        DB = secrets.database_url
        DONT_LOAD_DB = False
    except (ModuleNotFoundError, AttributeError):  # Probably running on travis, no need for real values here, but warn anyways
        print("Warn: Could not load DATABASE_URL, using bogus values.")
        DB = ""
        DONT_LOAD_DB = True

EOS_DATE = datetime(2023, 7, 1)

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
OAUTH_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Walk API. Currently: Strava
WALKAPI_SCOPES = [
    "read",
    "activity:read_all"
]


# For backup authentication service. Currently: auth0.com
# Should be used only until Google Cloud works again.
USE_BACKUP = False # Whether the backup auth servcce should be used
BACKUP_OAUTH_SCOPES = [
    "openid",
    "profile",
    "email"
]
try:
    BACKUP_CLIENT_ID = os.environ["BACKUP_CLIENT_ID"]
    BACKUP_CLIENT_SECRET = os.environ["BACKUP_CLIENT_SECRET"]
except:
    BACKUP_CLIENT_ID = ""
    BACKUP_CLIENT_SECRET = ""