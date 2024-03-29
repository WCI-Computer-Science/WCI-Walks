from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, request
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
        from .models.utils import update_tick, long_update_tick, get_ui_settings, fancy_float
        from .controllers import index, users, admin
        from .controllers.errors import error404, error500
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: update_tick(app.app_context()), 'cron', minute="*/1") # Thing that need to be polled
        scheduler.add_job(lambda: long_update_tick(app.app_context()), 'cron', hour="0") # Long function that could interupt normal functioning, like refreshing totals. Runs at 1am
        scheduler.start()

        # Create database and set up automatic database closing for requests
        database.init_app(app)

        # Route / to main page
        app.register_blueprint(index.bp)

        # Route /users to login and user statistics page
        app.register_blueprint(users.bp)

        # Route /admin to admin pages
        app.register_blueprint(admin.bp)

        app.context_processor(lambda: {"get_ui_settings": get_ui_settings, "fancy_float": fancy_float})

        # Route errors
        app.register_error_handler(404, error404)
        app.register_error_handler(500, error500)

    return app
