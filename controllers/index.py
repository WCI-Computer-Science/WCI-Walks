from flask import Blueprint, url_for, redirect, render_template, request, session
from templates.utils import get_all_time_leaderboard, get_day_leaderboard
from models import database
import datetime
bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def home():
    db = database.get_db()
    total = db.execute(
        'SELECT * FROM total'
    ).fetchone()
    return render_template(
        'index.html',
        alltimeleaderboard=get_all_time_leaderboard(),
        yesterdayleaderboard=get_day_leaderboard(datetime.date.today()-datetime.timedelta(days=1)),
        total=total
    )
