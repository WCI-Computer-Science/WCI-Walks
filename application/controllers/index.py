import datetime

from flask import Blueprint, render_template, current_app

from application.models import database
from application.templates.utils import (
    fancy_float,
    get_all_time_leaderboard,
    get_day_leaderboard,
)

bp = Blueprint("index", __name__, url_prefix="/")


@bp.route("/", methods=("GET",))
def home():
    db = database.get_db()
    with db.cursor() as cur:
        total = database.get_total(cur)[0]

    return render_template(
        "index.html",
        alltimeleaderboard=get_all_time_leaderboard(),
        yesterdayleaderboard=get_day_leaderboard(datetime.date.today()),
        total=fancy_float(total),
    )


@bp.route("/contact", methods=("GET",))
def contact():
    return render_template("contact.html", displayeos=(True if datetime.date.today() >= current_app.config["EOS_DATE"].date() else False))


@bp.route("/privacypolicy", methods=("GET",))
def privacypolicy():
    return render_template("privacypolicy.html")


@bp.route("/termsofservice", methods=("GET",))
def termsofservice():
    return render_template("termsofservice.html")


@bp.route("/help", methods=("GET",))
def userhelp():
    return render_template("help.html")