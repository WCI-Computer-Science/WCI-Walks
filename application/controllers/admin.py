from flask import abort, Blueprint, render_template, redirect, request
from application.templates.utils import isadmin, update_total, get_all_time_leaderboard
from flask_login import current_user, login_required

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
  update_total()
  if isadmin(current_user.get_id()):
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
def editdistances():
  return render_template("searchforuser.html")
