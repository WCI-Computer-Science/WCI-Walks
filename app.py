from flask import Flask, render_template, url_for

import secrets
from models import database
from controllers import userinfo

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = secrets.secret_key
app.config['DB'] = 'models/db.sqlite'

# Create database and set up automatic database closing for requests
database.init_app(app)

# Route / to main page
@app.route('/')
def index():
    return render_template('index.html')

# Route /users to login and user statistics page
app.register_blueprint(userinfo.bp)

# Test app for startup
if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')
