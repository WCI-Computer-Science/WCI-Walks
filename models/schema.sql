/* Initialize the database */

/* Total distance travelled as a school */
CREATE TABLE IF NOT EXISTS total (
    distance INTEGER
);

/* Info stored for each user:
    id: used to identify each submission of walk
    email: ensure user is part of WRDSB
    username: student's name
    distance: student's total distance
 */
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    distance INTEGER NOT NULL
);

/* Info stored for each walk (one walk stored per day):
    id: used to identify student who did walk
    distance: student's distance for that day
    walkdate: date of walk stored as YYYY-MM-DD
*/
CREATE TABLE IF NOT EXISTS walks (
    id INTEGER NOT NULL,
    distance INTEGER NOT NULL,
    walkdate TEXT NOT NULL
);