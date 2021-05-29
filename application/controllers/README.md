# Controllers
A description of each Blueprint and its URL is given in this file. All URLs are routed to a Blueprint.

# index
## URL: /
## Blueprint in _index.py_
### /
The / URL mount redirects to the main page. The main page contains the leaderboard that ranks the students, by total distance walked as well as distance walked any given day. All endpoints in the index blueprint stay the same regardless if a user is logged in or not.

### /privacypolicy
This page displays the site's privacy policy.

### /termsofservice
This page displays the site's terms of service.

### /contact
This page displays WCI Computer Science Club's contact information.

# users
## URL: /users
## Blueprint in _userinfo.py_
### /
The /users page allows a user to access their daily progress, personal statistics, and a form to log distance walked.
It has the following behaviour:
1. User is logged in:  
The user will be able to access their personal profile. If the user submits the distance from, the following occurs:  
    1. The form is valid (a number n such that 0 < n <= 300):  
    The distance is added to the database.
    2. The form is invalid:  
    An error is flashed.
2. User is not logged in:  
The user will be redirected to /users/login with a flashed error.

### /login
The /users/login page allows a user to log in to their account with Google's OAuth 2.0 API.
They must be part of the wrdsb.ca google organization.
If the user is already logged in, they will be redirected to /users.
Once clicking on the login button, users will be redirected to /users/authorize.

### /viewprofile/\<username\>
The /users/\<username\> page allows a logged-in user to see another person's basic walking statistics.
If the user is not logged in, they will be redirected to /users/login.

### /authorize
This page prepares a request and redirects to Google's login interface.
If the user is already logged in, they will be redirected to /users.
The user will log in, and Google will send back an authentication code to /users/authorize/confirmlogin.

### /authorize/confirmlogin
This page takes the code and swaps it for an authentication token, then verifies it and gets the user's information.
It then has the following behaviour:
1. User has a verified email and is part of WRDSB's organization:  
The user is logged in, the redirected to /users. If the user is not already in the database, it will automatically create a new account for them.
2. User fails to log in:  
An error is flashed and the user is redirected back to /users/login.

### /logout
The /users/logout page allows a user to log out of their account. It will log the user out of their account (resetting the cookie) and always redirects to the / home page.

# admin
## URL: /admin
## Blueprint in _admin.py_
All pages under this header check the table `admins`, and have the following behaviour:
1. User is in admins and has the column valid set to TRUE, it returns the page
2. Otherwise, it returns a 403 Forbidden error
### /
The / page returns a page of links linking to other admin pages.

### /updatetotal
The /updatetotal page triggers a program to re-calculate all assumed totals (user totals and the global total).

### /getuserlist
The /getuserlist page returns a JSON list of all usernames that contain the string from the argument `text`.

### /searchforuser
The /searchforuser page allows admins to search through all users.

### /edituserdistances/\<wrdsbusername\>
The /edituserdistances/\<wrdsbusername\> page allows admins to edit the distances that the user `wrdsbusername` has recorded

### /deleteuser/\<wrdsbusername\>
The /deleteuser/\<wrdsbusername\> page allows admins to delete any record of the user `wrdsbusername` from the tables `users` and `walks`. Anyone who meets all the conditions to access /admins cannot be deleted.
