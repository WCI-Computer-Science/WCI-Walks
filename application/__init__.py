from flask import Flask
import secrets, configs

def create_app():

    app = Flask(__name__)

    # Configurations
    app.config.from_object(configs)

    with app.app_context():
        from .models import database, loginmanager, oauth, user
        from .controllers import index, users
        # Create database and set up automatic database closing for requests
        database.init_app(app)

        # Route / to main page
        app.register_blueprint(index.bp)

        # Route /users to login and user statistics page
        app.register_blueprint(users.bp)

    return app

        
