import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DB'], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def teardown_db(err=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('models/schema.sql') as schema:
        db.executescript(schema.read().decode('utf8'))

@click.command('initdb')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('initialized db')

def init_app(app):
    app.teardown_appcontext(teardown_db)
    app.cli.add_command(init_db_command)
