from flask import Flask

app = Flask(__name__)

import secrets
from models import *
from controllers import index, users

# Configurations
app.config['SECRET_KEY'] = secrets.secret_key
app.config['SECURITY_PASSWORD_SALT'] = secrets.security_password_salt
app.config['DB'] = 'models/db.sqlite'
app.config['GOOGLE_CLIENT_ID'] = secrets.google_client_id
app.config['GOOGLE_CLIENT_SECRET'] = secrets.google_client_secret
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"


# Create database and set up automatic database closing for requests
database.init_app(app)

# Route / to main page
app.register_blueprint(index.bp)

# Route /users to login and user statistics page
app.register_blueprint(users.bp)

# Test app for startup
if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')
