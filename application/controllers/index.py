import datetime

from flask import Blueprint, url_for, redirect, render_template, request, session
from application.templates.utils import get_all_time_leaderboard, get_day_leaderboard, fancy_float

from application.models import database

bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=('GET',))
def home():
    db = database.get_db()
    with db.cursor() as cur:
        total = database.get_total(cur)[0]
    
    return render_template(
        'index.html',
        alltimeleaderboard=get_all_time_leaderboard(),
        yesterdayleaderboard=get_day_leaderboard(datetime.date.today()-datetime.timedelta(days=1)),
        total=fancy_float(total)
    )

@bp.route('/contact', methods=('GET',))
def contact():
    return render_template('contact.html')

@bp.route('/privacypolicy', methods=('GET',))
def privacypolicy():
    return render_template('privacypolicy.html')

@bp.route('/termsofservice', methods=('GET',))
def termsofservice():
    return render_template('termsofservice.html')
