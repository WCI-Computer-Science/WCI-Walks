/* Initialize the database */

/* Total distance travelled as a school */
CREATE TABLE IF NOT EXISTS total (
    distance NUMERIC(7,1)
);

/* Any announcements */
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    notice TEXT NOT NULL
);

/* Days to multiply */
CREATE TABLE IF NOT EXISTS multipliers (
    multiplydate DATE PRIMARY KEY,
    factor INT NOT NULL
);

/* Info stored for each user:
    id: used to identify each submission of walk
    email: ensure user is part of WRDSB
    username: student's name
    wrdsbusername: email without the @wrdsb.ca
    distance: student's total distance
    active: whether a user is active
    refreshtoken: OAuth refresh token
    googlefit: whether a user is connected with Google Fit
 */
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    wrdsbusername TEXT NOT NULL,
    distance NUMERIC(6,1) NOT NULL,
    position SMALLINT,
    likes SMALLINT,
    likediff SMALLINT,
    liked TEXT,
    active SMALLINT DEFAULT 1,
    refreshtoken TEXT,
    googlefit BOOLEAN DEFAULT FALSE
);

/* Info stored to see who is an admin:
    id: used to identify each person
    wrdsbusername: email without the @wrdsb.ca
    valid: whether a user is an admin
 */
CREATE TABLE IF NOT EXISTS admins (
    id TEXT PRIMARY KEY,
    wrdsbusername TEXT NOT NULL,
    valid SMALLINT DEFAULT 0
);

/* Info stored to see who is on the blacklist:
    id: used to identify each person
    wrdsbusername: email without the @wrdsb.ca
    valid: whether a user is an admin
 */
CREATE TABLE IF NOT EXISTS blacklist (
    id TEXT PRIMARY KEY,
    wrdsbusername TEXT NOT NULL,
    valid SMALLINT DEFAULT 0
);

/* Info stored for each walk (one walk stored per day):
    id: used to identify student who did the walk
    username: used to identify student who did the walk
    distance: student's distance for that day
    walkdate: date of walk stored as YYYY-MM-DD
    trackedwithfit: whether a walk was inputted by Google Fit
*/
CREATE TABLE IF NOT EXISTS walks (
    id TEXT NOT NULL,
    username TEXT NOT NULL,
    distance NUMERIC(6,1) NOT NULL,
    walkdate DATE NOT NULL,
    trackedwithfit BOOLEAN DEFAULT FALSE
);

/* Info about each team:
    teamname: randomly generated string of an adjective and a noun
    teamid: randomly generated string to identify the team
    joincode: 6-character randomly generated string, for users to join the team, can be NULL to indicate that no one can join the team
    members: comma-seperated string of user ids who are on the team
*/
CREATE TABLE IF NOT EXISTS teams (
    teamname TEXT UNIQUE NOT NULL,
    id SERIAL PRIMARY KEY,
    joincode TEXT,
    members TEXT NOT NULL
);