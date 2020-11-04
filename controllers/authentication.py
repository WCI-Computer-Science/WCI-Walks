import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from database import get_db

bp = Blueprint('auth', __name__, url_prefix='/users')

@bp.route('/', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def login():
    #etc