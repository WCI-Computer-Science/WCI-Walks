import datetime

from flask import Blueprint, render_template, current_app, Response

from flask_login import current_user

from application.models import database
from application.models.utils import (
    fancy_float,
    get_announcements,
    get_multipliers,
    get_all_time_leaderboard,
    get_day_leaderboard,
    get_all_time_team_leaderboard,
    get_day_team_leaderboard,
    get_ui_settings
)

bp = Blueprint("index", __name__, url_prefix="/")


@bp.route("/", methods=("GET",))
def home():
    db = database.get_db()
    with db.cursor() as cur:
        total = database.get_total(cur)
    
    multiplier = get_multipliers(date=datetime.date.today())
    if multiplier:
        multiplier = multiplier["factor"]

    return render_template(
        "index.html",
        announcements=get_announcements(),
        multiplier=multiplier,
        alltimeleaderboard=[[i[0] if len(i[0].split()) == 1 else ' '.join((i[0].split()[0], i[0].split()[-1])), i[1], i[2], i[3], i[4]] for i in get_all_time_leaderboard()],
        yesterdayleaderboard=[[i[0] if len(i[0].split()) == 1 else ' '.join((i[0].split()[0], i[0].split()[-1])), i[1], i[2]] for i in get_day_leaderboard(datetime.date.today())],
        alltimeteamleaderboard=get_all_time_team_leaderboard(),
        yesterdayteamleaderboard=get_day_team_leaderboard(datetime.date.today()),
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

@bp.route("/theme.css", methods=("GET",))
def themestyle():
    if current_user.is_authenticated:
        uiSettings = get_ui_settings(id=current_user.id)
    else:
        uiSettings = get_ui_settings()
    css = render_template("theme.css",
        themeR=uiSettings["themeR"],
        themeG=uiSettings["themeG"],
        themeB=uiSettings["themeB"])
    resp = Response(css, mimetype="text/css")
    return resp