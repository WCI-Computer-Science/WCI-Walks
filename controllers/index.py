from flask import Blueprint, redirect, render_template, request, session
from .utils import get_leaderboard
bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def home():
    return render_template('index.html', leaderboard=get_leaderboard())
