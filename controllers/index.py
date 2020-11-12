from flask import Blueprint, redirect, render_template, request, session
from templates.utils import get_all_time_leaderboard
bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def home():
    return render_template('index.html', alltimeleaderboard=get_all_time_leaderboard())
