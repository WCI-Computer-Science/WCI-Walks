import sys
from models import database

# note 1: hopefully in the future we could have an "online" ranking
# already in sorted order and add users with a log2 n binary search

def get_all_time_leaderboard():
    db = database.get_db()
    # 3 things
    # .fetchall already returns a list of Row objects (kind of like tuples)
    # builtin .sort method uses Timsort for O(nlogn), while bubble sort is pretty bad even among other O(n^2) functions
    userdistances = db.execute(
        "SELECT username, distance FROM users;"
    ).fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True)
    print(userdistances, file=sys.stderr)
    return userdistances

def get_day_leaderboard(date):
    db = database.get_db()
    userdistances = db.execute(
        "SELECT id, distance FROM walks WHERE walkdate=?;", (date,)
    ).fetchall()
    userdistances.sort(key=lambda user: user[1], reverse=True) 
    for i in range(len(userdistances)):
        userdistances[i]=list(userdistances[i])
        userdistances[i][0] = list(db.execute("SELECT username FROM users WHERE id=?;", (userdistances[i][0],)).fetchone())[0]
    return userdistances

