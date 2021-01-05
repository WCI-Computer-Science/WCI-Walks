/* Initialize the database */

/* Total distance travelled as a school */
CREATE TABLE IF NOT EXISTS total (
    distance REAL
);

/* Info stored for each user:
    id: used to identify each submission of walk
    email: ensure user is part of WRDSB
    username: student's name
    wrdsbusername: email without the @wrdsb.ca
    distance: student's total distance
    active: whether a user is active
 */
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    wrdsbusername TEXT NOT NULL,
    distance REAL NOT NULL,
    active SMALLINT DEFAULT 1
);

/* Info stored for each walk (one walk stored per day):
    id: used to identify student who did the walk
    username: used to identify student who did the walk
    distance: student's distance for that day
    walkdate: date of walk stored as YYYY-MM-DD
*/
CREATE TABLE IF NOT EXISTS walks (
    id TEXT NOT NULL,
    username TEXT NOT NULL,
    distance REAL NOT NULL,
    walkdate DATE NOT NULL
);