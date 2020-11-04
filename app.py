from flask import Flask, render_template

from models import database
from controllers import login

app = Flask(__name__)

# Create database and set up automatic database closing for requests
app.config['DB'] = 'models/db.sqlite'
database.init_app(app)

# Route / to main page
@app.route('/')
def index():
    return render_template('index.html')

# Route /users to login and user statistics page
app.register_blueprint(login.bp)

# Test app for startup
if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')