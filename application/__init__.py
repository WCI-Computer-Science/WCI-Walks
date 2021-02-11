from flask import Flask, request
import configs

def redirect_http_https():
    if request.is_secure:
        return
    url = request.url.replace("http://", "https://", 1)
    return redirect(url, 301)

def create_app():

    app = Flask(__name__)
    app.before_request(redirect_http_https)

    # Configurations
    app.config.from_object(configs)

    with app.app_context():
        from .models import database, loginmanager, oauth, user
        from .controllers import index, users, admin
        from .controllers.errors import error404, error500

        # Create database and set up automatic database closing for requests
        database.init_app(app)

        # Route / to main page
        app.register_blueprint(index.bp)

        # Route /users to login and user statistics page
        app.register_blueprint(users.bp)

        # Route /admin to admin pages
        app.register_blueprint(admin.bp)

        # Route errors
        app.register_error_handler(404, error404)
        app.register_error_handler(500, error500)

    return app
