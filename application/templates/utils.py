import sys
from application.models import database

# note 1: hopefully in the future we could have an "online" ranking
# already in sorted order and add users with a log2 n binary search

# note 2: only shows top 15 for all time, top 10 for yesterday's
# this does 2 things: makes sure first that if there's 100 students participating,
# there's not an outrageous amount of users displayed
# second, it reduces the max amount of items in the list so distances
# being passed to front end isn't huge

def get_all_time_leaderboard():
    db = database.get_db()
    with db.cursor() as cur:
        userdistances = db.execute(
            "SELECT username, distance FROM users;"
        ).fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    
    return userdistances[:15]

def get_day_leaderboard(date):
    db = database.get_db()
    with db.cursor() as cur:
        userdistances = db.execute(
            "SELECT username, distance FROM walks WHERE walkdate=?;", (date,)
        ).fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)

    return userdistances[:10]

