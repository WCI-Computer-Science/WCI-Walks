from flask import Flask

import secrets
from models import database
from controllers import *

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = secrets.secret_key
app.config['SECURITY_PASSWORD_SALT'] = secrets.security_password_salt
app.config['DB'] = 'models/db.sqlite'

# Create database and set up automatic database closing for requests
database.init_app(app)

# Route / to main page
app.register_blueprint(index.bp)

# Route /users to login and user statistics page
app.register_blueprint(userinfo.bp)

# Test app for startup
if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')
