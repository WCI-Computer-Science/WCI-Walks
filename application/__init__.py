from flask import Flask
import secrets

def create_app():

    app = Flask(__name__)

    # Configurations
    app.config['SECRET_KEY'] = secrets.secret_key
    app.config['SECURITY_PASSWORD_SALT'] = secrets.security_password_salt
    app.config['DB'] = 'models/db.sqlite'
    app.config['GOOGLE_CLIENT_ID'] = secrets.google_client_id
    app.config['GOOGLE_CLIENT_SECRET'] = secrets.google_client_secret
    app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

    with app.app_context():
        from models import database, loginmanager, oauth, user
        from controllers import index, users
        # Create database and set up automatic database closing for requests
        database.init_app(app)

        # Route / to main page
        app.register_blueprint(index.bp)

        # Route /users to login and user statistics page
        app.register_blueprint(users.bp)

    return app

        
