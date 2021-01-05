import sys
import ast
import json

from flask import abort, Blueprint, render_template, redirect, request
from application.templates.utils import isadmin, update_total, get_all_time_leaderboard, fancy_float, replace_walk_distances, get_credentials_from_wrdsbusername, user_exists
from flask_login import current_user, login_required
from application.models import database
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/")
@login_required
def adminhome():
  if not current_user.is_admin(): abort(403)
  return render_template("adminpage.html")

@bp.route("/updatetotal")
@login_required
def updatetotal():
  if not current_user.is_admin(): abort(403)
  update_total()
  return render_template("updatetotalsuccess.html")

@bp.route("/getuserlist")
def getuserlist():
  if not current_user.is_admin(): abort(403)
  search = request.args.get("text", "").lower()
  userlist = get_all_time_leaderboard()
  if search != "":
    userlist = [i for i in userlist if search in i[0].lower()]
  userlist.sort(key=lambda user:user[0])
  return json.dumps(userlist)

@bp.route("/searchforuser")
def searchforuser():
  if not current_user.is_admin(): abort(403)
  return render_template("searchforuser.html")

@bp.route("/edituserdistances/<wrdsbusername>", methods=("GET", "POST"))
@login_required
def editdistancespage(wrdsbusername):
  if not current_user.is_admin(): abort(403)
  if request.method == "POST":
    datetimedates = list()
    distances = list()
    dates = list()
    olddistances = ast.literal_eval(request.form.get("alldistances"))
    alldates = ast.literal_eval(request.form.get("alldates"))
    for i in alldates:
        distances.append(fancy_float(request.form.get(str(i))))
        datetimedates.append(i)
        dates.append(datetime.strptime(i, "%Y-%m-%d").strftime("%A, %B %d, %Y"))
    replace_walk_distances(distances, datetimedates, olddistances, current_user, id=get_credentials_from_wrdsbusername(wrdsbusername)[0])
    if olddistances!=distances:
        update_total()
  else:
    db = database.get_db()
    with db.cursor() as cur:
      datetimedates, distances = current_user.get_walk_chart_data(cur, id=get_credentials_from_wrdsbusername(wrdsbusername)[0])
    dates = list()
    distances = list(map(fancy_float, distances))
    for i in datetimedates:
      dates.append(i.strftime("%A, %B %d, %Y"))
  datetimedates = list(map(str, datetimedates))
  return render_template(
    "editdistance.html",
    distances=distances,
    dates=dates,
    datetimedates=datetimedates,
    user=get_credentials_from_wrdsbusername(wrdsbusername)[1])

@bp.route("/deleteuser/<wrdsbusername>", methods=("GET", "POST"))
def deleteuser(wrdsbusername):
  if not current_user.is_admin(): abort(403)
  if not user_exists(wrdsbusername): abort(404)
  if request.method=="POST":
    pass # Will fill this in later
  else:
    return render_template(
      "deleteuser.html",
      wrdsbusername=wrdsbusername
    )
