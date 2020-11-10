from models import database
def get_leaderboard():
    db = database.get_db()
    userdistances = list(db.execute("SELECT username, distance FROM users;").fetchall())

    for _ in range(len(userdistances) - 1):
        for i in range(len(userdistances) - 1):
            if userdistances[i][1] > userdistances[i + 1][1]:
                userdistances[i], userdistances[i + 1] = userdistances[i + 1], userdistances[i]
    for i in range(len(userdistances)):
        userdistances[i]=list(userdistances[i])
    return userdistances
