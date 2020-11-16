from flask import Flask
from oauthlib.oauth2 import WebApplicationClient

import secrets
from models import *
from controllers import index, userinfo

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = secrets.secret_key
app.config['SECURITY_PASSWORD_SALT'] = secrets.security_password_salt
app.config['DB'] = 'models/db.sqlite'
app.config['GOOGLE_CLIENT_ID'] = secrets.google_client_id
app.config['GOOGLE_CLIENT_SECRET'] = secrets.google_client_secret

# Create database and set up automatic database closing for requests
database.init_app(app)

client = WebApplicationClient(secrets.google_client_secret)

# Route / to main page
app.register_blueprint(index.bp)

# Route /users to login and user statistics page
app.register_blueprint(userinfo.bp)

# Test app for startup
if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')
