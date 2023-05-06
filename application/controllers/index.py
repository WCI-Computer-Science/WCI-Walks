import datetime

from flask import Blueprint, flash, jsonify, render_template, current_app, Response, send_file, request, abort, session

from flask_login import current_user

from io import BytesIO

from application.models import database
from application.models.utils import (
    fancy_float,
    get_announcements,
    get_multipliers,
    get_all_time_leaderboard,
    get_day_leaderboard,
    get_all_time_team_leaderboard,
    get_day_team_leaderboard,
    get_ui_settings,
    get_big_image
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
    uiSettings = get_ui_settings(consider_current_user=True)
    css = render_template("theme.css",
        themeR=uiSettings["themeR"],
        themeG=uiSettings["themeG"],
        themeB=uiSettings["themeB"])
    resp = Response(css, mimetype="text/css")
    resp.headers["Cache-Control"] = "no-cache"
    return resp

@bp.route("/bigimage.png", methods=("GET",))
def bigimage():
    if current_user.is_authenticated:
        bigimage, bigimagehash = get_big_image(id=current_user.id)
    else:
        bigimage, bigimagehash = get_big_image()
    if "If-None-Match" in request.headers:
        if request.headers["If-None-Match"] == bigimagehash:
            return Response(status=304)
    resp = send_file(BytesIO(bigimage), mimetype="image/png")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["ETag"] = bigimagehash
    return resp

@bp.route("/leaderboards", methods=("GET","POST"))
def full_page_leaderboards():
    # This isn't intended to actually be secure, more as a deterrent from people randomly accessing it, as
    # the page makes regular requests to keep the leaderboard up to date, which most people don't need.
    uiSettings = get_ui_settings(consider_current_user=True)
    password = uiSettings["leaderboardPassword"]
    needs_password = True
    if "leaderboardPassword" in session and session["leaderboardPassword"] == password:
        needs_password = False
    if request.method == "POST":
        reqPassword = request.form.get("password")
        if reqPassword == password:
            # Because this doesn't need to be totally secure, stick the password in session
            # Session isn't accessible without the APP_KEY anyways, so this isn't a major issue
            session["leaderboardPassword"] = password
            needs_password = False
        else:
            flash("Incorrect password")

    return render_template("leaderboards.html", needs_password=needs_password)

@bp.route("/leaderboards/<leaderboard_name>", methods=("GET",))
def leaderboard_data(leaderboard_name):
    """
    alltimeleaderboard=[[i[0] if len(i[0].split()) == 1 else ' '.join((i[0].split()[0], i[0].split()[-1])), i[1], i[2], i[3], i[4]] for i in get_all_time_leaderboard()],
    yesterdayleaderboard=[[i[0] if len(i[0].split()) == 1 else ' '.join((i[0].split()[0], i[0].split()[-1])), i[1], i[2]] for i in get_day_leaderboard(datetime.date.today())],
    alltimeteamleaderboard=get_all_time_team_leaderboard(),
    yesterdayteamleaderboard=get_day_team_leaderboard(datetime.date.today()),
    """
    if "leaderboardPassword" not in session or session["leaderboardPassword"] != get_ui_settings(consider_current_user=True)["leaderboardPassword"]:
        abort(403)
    if leaderboard_name == "alltimeleaderboard":
        return jsonify([[i[0] if len(i[0].split()) == 1 else ' '.join((i[0].split()[0], i[0].split()[-1])), i[1], i[2], i[3], i[4]] for i in get_all_time_leaderboard()])
    elif leaderboard_name == "yesterdayleaderboard":
        return jsonify([[i[0] if len(i[0].split()) == 1 else ' '.join((i[0].split()[0], i[0].split()[-1])), i[1], i[2]] for i in get_day_leaderboard(datetime.date.today())])
    elif leaderboard_name == "alltimeteamleaderboard":
        return jsonify(get_all_time_team_leaderboard())
    elif leaderboard_name == "yesterdayteamleaderboard":
        return jsonify(get_day_team_leaderboard(datetime.date.today()))
    abort(404)