from flask import abort, Blueprint, render_template, redirect, request
from application.templates.utils import isadmin, update_total, get_all_time_leaderboard, fancy_float, replace_walk_distances
from flask_login import current_user, login_required
from application.models import database
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/")
@login_required
def adminhome():
  if isadmin(current_user.get_id()):
    return render_template("adminpage.html")
  else: abort(403)

@bp.route("/updatetotal/")
@login_required
def updatetotal():
  if isadmin(current_user.get_id()):
    update_total()
    return render_template("updatetotalsuccess.html")
  else: abort(403)

@bp.route("/getuserlist/")
def getuserlist():
  search = request.args.get("text", "")
  userlist = get_all_time_leaderboard()
  returnlist = list(userlist) # Using list() to seperate from userlist, otherwise returnlist would be tied to userlist
  if search != "":
    for i in userlist:
      if search not in i[0]:
        returnlist.remove(i)
    returnlist.sort(key=lambda user:user[0])
  return render_template("userlist.html", userlist=returnlist)

@bp.route("/searchforuser/")
def searchforuser():
  return render_template("searchforuser.html")

@bp.route("/edituserdistances/<wrdsbusername>", methods=("GET", "POST"))
@login_required
def editdistancespage(wrdsbusername):
  if not current_user.is_admin(): abort(403)
  if request.method == "POST":
    datetimedates = list()
    distances = list()
    dates = list()
    olddistances = eval(request.form.get("alldistances"))
    alldates = eval(request.form.get("alldates"))
    for i in alldates:
        distances.append(fancy_float(request.form.get(str(i))))
        datetimedates.append(i)
        dates.append(datetime.strptime(i, "%Y-%m-%d").strftime("%A, %B %d, %Y"))
    replace_walk_distances(distances, datetimedates, olddistances, current_user)
    if olddistances!=distances:
        update_total()
  else:
    db = database.get_db()
    with db.cursor() as cur:
      datetimedates, distances = current_user.get_walk_chart_data(cur)
    dates = list()
    distances = list(map(fancy_float, distances))
    for i in datetimedates:
      dates.append(i.strftime("%A, %B %d, %Y"))
  datetimedates = list(map(str, datetimedates))
  return render_template("editdistance.html", distances=distances, dates=dates, datetimedates=datetimedates, user=current_user.username)
