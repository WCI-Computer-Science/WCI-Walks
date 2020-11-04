import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from models import database

bp = Blueprint('auth', __name__, url_prefix='/users')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def login():
    return render_template('users.html')

@bp.route('/sign-up', methods=('GET', 'POST'))
def signup():
    return render_template('users.html') #fix later