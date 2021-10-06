import datetime, sys, requests

from flask import (
    abort,
    Blueprint,
    flash,
    Markup,
    redirect,
    render_template,
    request,
    url_for,
    session
)
from flask_login import current_user, login_required, login_user, logout_user
from wtforms import (
    DecimalField,
    Form,
    SubmitField,
    validators,
)

from application.models import *
from application.models.utils import (
    add_to_total,
    add_to_team,
    autoload_day,
    cap_distance,
    create_team,
    get_credentials_from_wrdsbusername,
    haspayed,
    isadmin,
    isblacklisted,
    getteamname_from_id,
    join_team,
    new_join_code,
    verify_walk_form,
    walk_is_maxed,
    walk_will_max_distance
)

bp = Blueprint("users", __name__, url_prefix="/users")


class SubmitDistanceForm(Form):
    distance = DecimalField("Log your walk distance (in km)", places=2)
    submit = SubmitField()


@bp.route("/", methods=("GET", "POST"))
@login_required
def info():
    db = database.get_db()
    date = datetime.date.today()
    form = SubmitDistanceForm(request.form)

    if request.method == "POST":
        form.distance.validators = [
            validators.InputRequired(),
            validators.NumberRange(
                min=0.01,
                max=300,
                message="Invalid distance"
            ),
            walk_is_maxed(current_user.get_id(), max=300),
        ]
        if verify_walk_form(form, current_user.id)==True:
            with db.cursor() as cur:
                walk = current_user.get_walk(date, cur)
                
                walkwillmaxdistance = walk_will_max_distance(
                    float(form.distance.data), current_user.get_id()
                )
                distance = round(
                    (
                        float(cap_distance(form.distance.data, current_user.id))
                    ),
                    1,
                )

                current_user.update_walk(distance, date, walk, cur)

                add_to_total(distance, cur)
                add_to_team(distance, current_user.team_id(), cur)

                current_user.add_distance(distance)
                current_user.update_distance_db(cur)

            db.commit()
            if walkwillmaxdistance:
                if distance > 0:
                    flash(
                        "Your walk was partly recorded. You can't go more than 300 km per day."
                    )
                else:
                    flash(
                        "You walk was partly recorded. You can't go less than 0 km per day."
                    )
            else:
                flash(
                    "You've successfully updated the distance!"
                )

        else:
            if request.form.get("extension", None) != None:
                return verify_walk_form(form, current_user.id)
            else:
                flash(
                  verify_walk_form(form, current_user.id)
                )


    with db.cursor() as cur:
        labels, data = current_user.get_walk_chart_data(cur)

    return render_template(
        "users.html",
        username=current_user.username,
        distance=current_user.distance,
        form=form,
        labels=labels,
        data=data,
    )

# Get information about the team you're on, if you're not on a team, put buttons to join a team and create a team
@bp.route("/teams")
@login_required
def getteampage():
    teamdata = current_user.team_name(joincode=True)
    if teamdata is None: # User is not in a team, send them to teamjoin
        return render_template("teamjoin.html")
    else: # User is in a team, send them to their team's homepage
        return render_template (
            "teampage.html",
            yourteam=True,
            teamdata=teamdata,
            teamid=current_user.team_id(),
            members=get_team_member_names(userid=current_user.get_id())
        )

@bp.route("/viewteam/<teamid>")
@login_required
def viewteam(teamid):
    # If user is part of that team, redirect them to main teams page
    if str(current_user.team_id()) == teamid:
        return redirect("/users/teams")
    teamdata = getteamname_from_id(teamid)
    if teamdata is None: # Ensure team exists
        abort(404)
    return render_template(
        "teampage.html",
        teamdata=teamdata,
        teamid=teamid,
        members=get_team_member_names(teamid=teamid)
    )

# Page that asks for a join code for a team
@bp.route("/teams/join", methods=("POST",))
@login_required
def jointeam():
    if not join_team(current_user.get_id(), joincode=request.form.get("joincode", None)):
        # The join code was invalid, flash an error
        flash("Sorry, that's not a valid join code. Please try again.")
    return redirect("/users/teams")

# Page that lets you leave the team you're on
@bp.route("/teams/leave", methods=("GET", "POST"))
@login_required
def leaveteam():
    join_team(current_user.get_id())
    return redirect("/users/teams")

@bp.route("/togglegooglefit")
@login_required
def togglegooglefit():
    db = database.get_db()
    with db.cursor() as cur:
        current_user.toggle_googlefit(current_user.id, cur)
    db.commit()
    return redirect("/users")


@bp.route("/like/<wrdsbusername>")
@login_required
def likesomeone(wrdsbusername):
    db = database.get_db()
    with db.cursor() as cur:
        try:
            userid, name = get_credentials_from_wrdsbusername(
                wrdsbusername, cur
            )
        except TypeError:
            return render_template(
                "error.html",
                text="Sorry, we couldn't find any record of "
                + str(wrdsbusername)
                + " in our database.",
            )
    current_user.like(userid)
    return redirect("/users/viewprofile/"+wrdsbusername, 302)

@bp.route("/unlike/<wrdsbusername>")
@login_required
def unlikesomeone(wrdsbusername):
    db = database.get_db()
    with db.cursor() as cur:
        try:
            userid, name = get_credentials_from_wrdsbusername(
                wrdsbusername, cur
            )
        except TypeError:
            return render_template(
                "error.html",
                text="Sorry, we couldn't find any record of "
                + str(wrdsbusername)
                + " in our database.",
            )
    current_user.unlike(userid)
    return redirect("/users/viewprofile/"+wrdsbusername, 302)

@bp.route("/viewprofile/<wrdsbusername>", methods=("GET", "POST"))
@login_required
def viewprofile(wrdsbusername):
    db = database.get_db()
    with db.cursor() as cur:
        try:
            userid, name = get_credentials_from_wrdsbusername(
                wrdsbusername,
                cur
            )
            labels, data = current_user.get_walk_chart_data(cur, id=userid)
        except TypeError:
            cur.close()
            return render_template(
                "error.html",
                text="Sorry, we couldn't find any record of "
                + str(wrdsbusername)
                + " in our database.",
            )
    return render_template(
        "otherusers.html",
        labels=labels,
        data=data,
        name=name,
        wrdsbusername=wrdsbusername,
        userid=userid,
    )

@bp.route("/loggedin")
def loggedin():
    if current_user.is_authenticated:
        return "{'loggedin':true}"
    else:
        return "{'loggedin':false}"

@bp.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.info"))

    return render_template("userlogin.html")


@bp.route("/authorize", methods=("GET", "POST"))
def authorize():
    if current_user.is_authenticated:
        return redirect(url_for("users.info"))

    # Backup Auth ###
    if current_app.config.get("USE_BACKUP"):
        backup_auth_url = oauth.backup_get_auth_url()
        return redirect(backup_auth_url)

    auth_url = oauth.get_auth_url()
    return redirect(auth_url)


@bp.route("/authorize/confirmlogin", methods=("GET", "POST"))
def confirmlogin():
    try:
        code = request.args.get("code")

        # Normal Auth
        if not current_app.config.get("USE_BACKUP"):
            token, refresh = oauth.get_access_token(code)
            idinfo = oauth.get_id_info(token)

            if idinfo.get("email_verified") and idinfo.get("hd") == "wrdsb.ca":
                email = idinfo["email"]
                username = idinfo["name"]
                userid = email.split("@")[0] + idinfo["given_name"].lower()
            else:
                flash("Email invalid. Are you using your WRDSB email?")
                return redirect(url_for("users.login"))
        # Backup auth
        else:
            token, refresh = oauth.backup_get_access_token(code)
            idinfo = oauth.backup_get_id_info(token)
        
            if idinfo.get("email_verified") and idinfo.get("email")[-8:] == "wrdsb.ca":
                email = idinfo["email"]
                username = idinfo["name"]
                userid = email.split("@")[0] + idinfo["given_name"].lower()
            else:
                flash("Email invalid. Are you using your WRDSB email?")
                return redirect(url_for("users.login"))

        db = database.get_db()
        if isblacklisted(userid, email):
            flash(
                "You have been banned from WCI Walks and cannot create an account or log in. Please contact us if you think this is a mistake."
            )
            return redirect(url_for("users.login"))
        if not(haspayed(email)) and not (haspayed("all")) and not(isadmin(userid)):
            flash(Markup(
                "You need to pay the participation fee before you can track your walks! Please email <a href=\"mailto:haos8097@wrdsb.ca\" target=\"_blank\">Scott</a> if you've already done so."
            ))
            return redirect(url_for("users.login"))
        with db.cursor() as cur:
            if not user.User.exists(userid, cur):
                current_user = user.User(
                    userid=userid,
                    email=email,
                    username=username
                )
                current_user.write_db(cur)
                if refresh:
                    current_user.add_refresh(refresh, cur)
                elif not current_app.config.get("USE_BACKUP"):
                    return redirect(oauth.get_auth_url() + "&prompt=consent")
                    # This should only happen if the refresh token is lost
                    # due to deleting and re-adding user, server crash, etc
            else:
                current_user = user.User(userid=userid)
                current_user.read_db(cur)
                if not oauth.get_refresh(current_user.id):
                    if refresh:
                        current_user.add_refresh(refresh, cur)
                    elif not current_app.config.get("USE_BACKUP"):
                        return redirect(oauth.get_auth_url() + "&prompt=consent")
                        # Same situations as above
            db.commit()

        login_user(current_user)
        return redirect(url_for("users.info"))

    except:
        # Probably entered URL by mistake
        return redirect(url_for("users.login"))


# Authorize the walking API for the user
# Currently: Strava
@bp.route("/authorizewalk", methods=("GET", "POST"))
@login_required
def authorizewalk():
    auth_url = oauth.walkapi_get_auth_url()
    print(auth_url)
    return redirect(auth_url)


@bp.route("/authorizewalk/confirmlogin", methods=("GET", "POST"))
@login_required
def confirmwalklogin():
    try:
        code = request.args.get("code")
        token, refresh, expiresat, athlete = oauth.walkapi_get_access_token(code)
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE users SET
                walkapi_accesstoken=%s,
                walkapi_refreshtoken=%s,
                walkapi_expiresat=%s,
                walkapi_id=%s 
                WHERE id=%s
                """,
                (token, refresh, expiresat, athlete["id"], current_user.id)
            )
            current_user.toggle_googlefit(current_user.id, cur, val=True)
            db.commit()
    except:
        flash("Something went wrong logging you in. Please try again.")
    
    return redirect(url_for("users.info"))


# Endpoint for webhook to load distance for a user
# Distance information is not included with the webhook notification
# However, we can simply only update a user's distance information on a webhook ping
@bp.route("/walkwebhook", methods=("GET", "POST"))
def loaddistance():
    if request.method == "GET":
        if request.args.get("hub.verify_token") != current_app.config["WALKAPI_WEBHOOK_SECRET"]:
            print("VERIFY WEBHOOK FAILED. ABORT.")
            abort(404)
        return {"hub.challenge": request.args.get("hub.challenge")}
    else:
        if str(request.json.get("subscription_id")) != str(current_app.config["WALKAPI_WEBHOOK_SUBSCRIPTION_ID"]):
            print("VERIFY WEBHOOK FAILED. ABORT.")
            abort(404)
        
        print("Webhook received")
        ownerid = str(request.json["owner_id"])
        db = database.get_db()
        with db.cursor() as cur:
            cur.execute("SELECT id, username, email FROM users WHERE walkapi_id=%s", (ownerid,))
            userid, username, email = cur.fetchone()
            print(ownerid, userid)
            if (
                request.json["object_type"] == "athlete" and
                "authorized" in request.json["updates"] and
                request.json["updates"]["authorized"] == False
            ):
                print("Revoking access")
                oauth.walkapi_disconnect(userid, cur)
            elif (
                request.json["object_type"] == "activity" and
                request.json["aspect_type"] == "create"
            ):
                autoload_day(userid, username, email, datetime.date.today(), cur)
        db.commit()
        return {"message": "ok"}


@bp.route("/logout", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
@login_required
def logout():
    logout_user()
    # add a log out view in the future
    return redirect(url_for("index.home"))
