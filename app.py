from flask import Flask

from flask_mail import Mail, Message

import secrets
from models import database
from controllers import *

app = Flask(__name__)
mail = Mail(app)

# Configurations
app.config['SECRET_KEY'] = secrets.secret_key
app.config['SECURITY_PASSWORD_SALT'] = secrets.security_password_salt
app.config['DB'] = 'models/db.sqlite'

# Mail configurations
mailconfigs = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": secrets.emailuser,
    "MAIL_PASSWORD": secrets.emailpassword
}
app.config.update(mailconfigs)

# Create database and set up automatic database closing for requests
database.init_app(app)

# Route / to main page
app.register_blueprint(index.bp)

# Route /users to login and user statistics page
app.register_blueprint(userinfo.bp)

# Test app for startup
if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')
