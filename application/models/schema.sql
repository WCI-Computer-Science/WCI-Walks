/* Initialize the database */

/* General information used by the app:
   distance: total distance travelled as a school
   load_pointer: index of student being loaded (see autoload_day_all function for details)
*/
CREATE TABLE IF NOT EXISTS total (
    distance NUMERIC(7,1),
    load_pointer INT NOT NULL DEFAULT 0
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

/* Eligible users */
CREATE TABLE IF NOT EXISTS payed (
    email TEXT UNIQUE
)

/* Info stored for each user:
    id: used to identify each user
    email: ensure user exists and is part of WRDSB
    username: student's name
    wrdsbusername: email without the @wrdsb.ca
    distance: student's total distance
    position: position on leaderboard
    likes, likediff, liked: part of liking system
    active: whether a user is active
    refreshtoken: OAuth refresh token
    walkapi_id: ID of the user in the walking API (currently Strava)
    walkapi_refreshtoken: OAuth refresh token for walking API
    walkapi_accesstoken: OAuth access token for walking API
    walkapi_expiresat: Expiry time of walkapi_accesstoken
    googlefit: whether a user is connected with walking API (NOT necessarily Google Fit)
    teamid: the ID of the team the user's on
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
    walkapi_id TEXT,
    walkapi_refreshtoken TEXT,
    walkapi_accesstoken TEXT,
    walkapi_expiresat BIGINT,
    googlefit BOOLEAN DEFAULT FALSE,
    teamid INT
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
    id: used to identify the team
    teamname: randomly generated string of an adjective and a noun
    distance: sum of users' distances
    joincode: 6-character randomly generated string, for users to join the team, can be NULL to indicate that no one can join the team
*/
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    teamname TEXT UNIQUE NOT NULL,
    distance NUMERIC(7,1) NOT NULL DEFAULT 0,
    joincode TEXT
);

/* Members who are part of each team:
    id: identify the team
    memberid: identify the user who is a member
*/
CREATE TABLE IF NOT EXISTS team_members (
    id INT NOT NULL,
    memberid TEXT UNIQUE NOT NULL
);