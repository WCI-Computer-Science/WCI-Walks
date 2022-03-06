# Connects to database

import datetime, json
import redis

import psycopg2
import psycopg2.extras
from flask import current_app, g


# Get database from sqlite connect method
def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            current_app.config["DB"],
            sslmode="require",
            cursor_factory=psycopg2.extras.DictCursor,
        )

    return g.db


# Close the database connection
def teardown_db(err=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Redis client will automatically close itself, no teardown function needed
def get_redis():
    if "r" not in g:
        g.r = redis.Redis.from_url(
            current_app.config["REDIS"],
            decode_responses=True # Convert byte responses into strings
        )

    return g.r


# Close database after every request, register command line command
def init_app(app):
    app.teardown_appcontext(teardown_db)


# Get total from database
def get_total(cur):
    cur.execute("SELECT distance FROM total;")
    return cur.fetchone()[0]
