import ast, json
from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request
from flask_login import current_user, login_required

from application.models import *
from application.models.utils import (
    add_to_total,
    add_to_team,
    getteamid,
    edit_distance_update,
    fancy_float,
    get_all_time_leaderboard,
    get_credentials_from_wrdsbusername,
    get_edit_distance_data,
    get_announcements,
    get_multipliers,
    isadmin,
    update_total,
    multiply_by_factor
)

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def adminhome():
    if not current_user.is_admin():
        abort(403)
    return render_template("adminpage.html")

@bp.route("/updatetotal")
@login_required
def updatetotal():
    if not current_user.is_admin():
        abort(403)
    update_total()
    return render_template("updatetotalsuccess.html")



@bp.route("/getuserlist")
@login_required
def getuserlist():
    if not current_user.is_admin():
        abort(403)
    search = request.args.get("text", "").lower()
    userlist = [i for i in get_all_time_leaderboard() if search in i[0].lower()]
    userlist.sort(key=lambda user: user[0])
    return json.dumps(userlist)

@bp.route("/getpaymentlist")
@login_required
def getpaymentlist():
    if not current_user.is_admin():
        abort(403)
    search = request.args.get("text", "").lower()
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM payed;")
        paymentlist = [i[0].replace("@wrdsb.ca", "") for i in cur.fetchall() if search in i[0].lower()]
    return json.dumps(paymentlist)

@bp.route("/getannouncementlist")
@login_required
def getannouncementlist():
    if not current_user.is_admin():
        abort(403)
    return json.dumps([dict(i) for i in get_announcements()])

@bp.route("/getmultiplierlist")
@login_required
def getmultiplierlist():
    if not current_user.is_admin():
        abort(403)
    res = []
    for i in get_multipliers():
        multiplier = {}
        multiplier["multiplydate"] = str(i["multiplydate"])
        multiplier["factor"] = i["factor"]
        res.append(multiplier)
    return json.dumps(res)



@bp.route("/searchforuser")
@login_required
def searchforuser():
    if not current_user.is_admin():
        abort(403)
    return render_template("searchforuser.html")

@bp.route("/editpayments")
@login_required
def editpayments():
    if not current_user.is_admin():
        abort(403)
    return render_template("editpayments.html")

@bp.route("/editannouncements")
@login_required
def editannouncements():
    if not current_user.is_admin():
        abort(403)
    return render_template("editannouncements.html")

@bp.route("/editmultipliers")
@login_required
def editmultipliers():
    if not current_user.is_admin():
        abort(403)
    return render_template("editmultipliers.html")



@bp.route("/addpayment/<wrdsbusername>", methods=("GET",))
@login_required
def addpayment(wrdsbusername):
    if not current_user.is_admin():
        abort(403)

    email = wrdsbusername + "@wrdsb.ca"
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM payed WHERE email=%s LIMIT 1;",
            (email,)
        )
        if cur.fetchone():
            flash("User payment already added!")
            return redirect("/admin/editpayments")
        else:
            cur.execute(
                "INSERT INTO payed VALUES (%s)",
                (email,)
            )
    db.commit()
    flash("User payment successfully added!")
    return redirect("/admin/editpayments")

@bp.route("/deletepayment/<wrdsbusername>", methods=("GET",))
@login_required
def deletepayment(wrdsbusername):
    if not current_user.is_admin():
        abort(403)

    email = wrdsbusername + "@wrdsb.ca"
    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM payed WHERE email=%s LIMIT 1;",
            (email,)
        )
        if not cur.fetchone():
            flash("User does not exist!")
            return redirect("/admin/editpayments")
        else:
            cur.execute(
                "DELETE FROM payed WHERE email=%s",
                (email,)
            )
    db.commit()
    flash("User payment successfully deleted!")
    return redirect("/admin/editpayments")

@bp.route("/addannouncement/<announcement>", methods=("GET",))
@login_required
def addannouncement(announcement):
    if not current_user.is_admin():
        abort(403)

    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO announcements (notice) VALUES (%s)",
            (announcement,)
        )
    db.commit()
    flash("Announcement successfully added!")
    return redirect("/admin/editannouncements")

@bp.route("/deleteannouncement/<announcementID>", methods=("GET",))
@login_required
def deleteannouncement(announcementID):
    if not current_user.is_admin():
        abort(403)

    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM announcements WHERE id=%s",
            (announcementID,)
        )
    db.commit()
    flash("Announcement successfully deleted!")
    return redirect("/admin/editannouncements")

#TODO: make this more robust
@bp.route("/addmultiplier", methods=("GET",))
@login_required
def addmultiplier():
    if not current_user.is_admin():
        abort(403)

    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO multipliers (multiplydate, factor) VALUES (%s, %s)",
            (request.args.get('date'), request.args.get('factor'))
        )
    db.commit()
    flash("Multiplier successfully added!")
    return redirect("/admin/editmultipliers")

#TODO: make this more robust
@bp.route("/deletemultiplier", methods=("GET",))
@login_required
def deletemultiplier():
    if not current_user.is_admin():
        abort(403)

    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM multipliers WHERE multiplydate=%s",
            (request.args.get('date'),)
        )
    db.commit()
    flash("Multiplier successfully deleted!")
    return redirect("/admin/editmultipliers")



@bp.route("/edituserdistances/<wrdsbusername>", methods=("GET", "POST"))
@login_required
def newedituserdistancespage(wrdsbusername):
    if not current_user.is_admin():
        abort(403)

    if request.method == "GET":
        userdata = get_edit_distance_data(wrdsbusername)
        userdata = list(map(lambda a: [a[0], fancy_float(a[1]), a[2], a[0].strftime("%A, %B %d, %Y")], userdata))
        userid, username = get_credentials_from_wrdsbusername(wrdsbusername)
        return render_template(
            "editdistances.html",
            userdata=userdata,
            username=username,
            wrdsbusername=wrdsbusername,
        )
    else:
        distance = float(request.form.get("distance"))
        date = request.form.get("date")
        edit_distance_update(distance, date, wrdsbusername)
        return ""

@bp.route("/deleteuser/<wrdsbusername>", methods=("GET", "POST"))
@login_required
def deleteuser(wrdsbusername):
    if not current_user.is_admin():
        abort(403)

    db = database.get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM users WHERE wrdsbusername=%s LIMIT 1;",
            (wrdsbusername,)
        )
        user = cur.fetchone()
        if not user:
            abort(404)
    if request.method == "POST":
        if isadmin(user["id"]):
            flash(
                "You can't delete the account of an active admin! Have Tristan or Scott revoke their admin powers first."
            )
        elif request.form.get("confirm") == wrdsbusername:
            db = database.get_db()
            with db.cursor() as cur:
                if request.form.get("ban") == "on":
                    cur.execute(
                        """
                            INSERT INTO blacklist
                            (id, wrdsbusername, valid)
                            VALUES (%s, %s, %s)
                        """,
                        (
                            user["id"],
                            wrdsbusername,
                            True,
                        ),
                    )
                if request.form.get("unpay") == "on":
                    cur.execute("DELETE FROM payed WHERE email=%s", (user["email"],))
                add_to_total(-user["distance"], cur)
                add_to_team(-user["distance"], getteamid(user["id"]), cur)
                cur.execute("DELETE FROM users WHERE id=%s;", (user["id"],))
                cur.execute("DELETE FROM walks WHERE id=%s;", (user["id"],))
            db.commit()
            return redirect("/admin"), 303
        else:
            flash("You did not type the correct name!")

    return render_template(
        "deleteuser.html",
        username=user["username"],
        wrdsbusername=wrdsbusername
    )
