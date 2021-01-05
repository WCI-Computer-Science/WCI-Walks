# Connects to database

import psycopg2
import psycopg2.extras
import click
import time

from flask import current_app, g
from flask.cli import with_appcontext
from application.templates.utils import is_blocked

# Get database from sqlite connect method
def get_db():
    while is_blocked():
        time.sleep(2)
    if 'db' not in g:
        g.db = psycopg2.connect(
            current_app.config['DB'],
            sslmode='require',
            cursor_factory=psycopg2.extras.DictCursor
        )

    return g.db

# Close the database
def teardown_db(err=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize the database (first time use only)
def init_db():
    db = get_db()
    with open('schema.sql', 'r') as schema:
        with db.cursor() as cur:
            cur.execute(schema.read().decode('utf8'))
    db.commit()

# Close database after every request, register command line command
def init_app(app):
    app.teardown_appcontext(teardown_db)

# Get total from database
def get_total(cur):
    cur.execute(
        'SELECT * FROM total'
    )
    return cur.fetchone()
