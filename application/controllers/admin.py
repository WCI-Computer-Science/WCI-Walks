from flask import abort, Blueprint, render_template
from application.templates.utils import isadmin
from flask_login import current_user, login_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/")
@login_required
def adminhome():
  if isadmin(current_user.get_id()):
   return render_template("adminpage.html")
  else: abort(403)
