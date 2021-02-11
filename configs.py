import os

try:
    import secrets

    SECRET_KEY = secrets.secret_key
    GOOGLE_CLIENT_ID = secrets.google_client_id
    GOOGLE_CLIENT_SECRET = secrets.google_client_secret
except (ModuleNotFoundError, AttributeError):
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
        GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
    except KeyError:  # Probably running on travis, no need for real values here, but warn anyways
        print("Warn: Could not load secrets, using bogus values.")
        SECRET_KEY = ""
        GOOGLE_CLIENT_ID = ""
        GOOGLE_CLIENT_SECRET = ""
        
try:
    import secrets

    DB = os.environ["DATABASE_URL"]
except KeyError:
    try:
        DB = secrets.database_url
    except (ModuleNotFoundError, AttributeError):  # Probably running on travis, no need for real values here, but warn anyways
        print("Warn: Could not load DATABASE_URL, using bogus values.")
        DB = ""
        DONT_LOAD_DB = True

try:
    DB = os.environ["DATABASE_URL"]
    DONT_LOAD_DB = False
except KeyError:  # Probably running on travis, no need for real values here, but warn anyways.
    print("Warn: Could not load DATABASE_URL, using bogus values.")
    DB = ""
    DONT_LOAD_DB = True
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
