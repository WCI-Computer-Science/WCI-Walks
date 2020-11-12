from models import database

# note 1: hopefully in the future we could have an "online" ranking
# already in sorted order and add users with a log2 n binary search

def get_all_time_leaderboard():
    db = database.get_db()
    # 3 things
    # dict.items builtin 3 times faster than list(dict) function
    # builtin .sort method uses Timsort for O(nlogn), while bubble sort is pretty bad even among other O(n^2) functions
    # no need to convert to list, tuple is iterable
    userdistances = sorted(db.execute(
        "SELECT username, distance FROM users;"
    ).fetchall(), key=lambda user: user[1], reverse=True)
    return userdistances

def get_day_leaderboard(date):
    db = database.get_db()
    userdistances = sorted(db.execute(
        "SELECT id, distance FROM walks WHERE walkdate=?;", (date,)
    ).fetchall(), key=lambda user: user[1], reverse=True)
    for i in range(len(userdistances)):
        userdistances[i]=list(userdistances[i])
        userdistances[i][0] = list(db.execute("SELECT username FROM users WHERE id=?;", (userdistances[i][0],)).fetchone())[0]
    return userdistances

