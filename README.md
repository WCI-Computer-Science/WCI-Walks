# WCI Walks

## About this app
WCI Walks tracks the walkathon progress of students at WCI. It tracks individual as well as total progress.

Each student can sign up for an account, and then log in.
Once logged in, they can access user-specific information. This includes the distance they walked on different days, whether they're on the leaderboard, personal statistics, etc. They will also be able to input the distance they walk each day and see other users' progress.

Basic information is displayed on the main page. This includes a leaderboard ranking the people who have walked the most all-time, as well as for the previous day.

## Run this app
As of the time of writing, you can access the app on this URL: https://wciwalks.herokuapp.com.
Alternatively, you can run the app locally for testing.
Before testing, you must have a couple things set up.

First, ensure you have PostgreSQL installed and have a database set up.
Then ensure you have created a file called secrets.py with the following variables declared:
```python
secret_key = # Put your secure code for signing cookies
google_client_id = # Put the Client ID of your Google Oauth web application
google_client_secret = # Put the Client Secret of your Google Oauth web application
```

After that, follow the instructions below.

1. clone repo to your device
2. create a python3 virtual environment
```bash
python3 -m venv _path_to_virtual_env_
```
3. activate the venv
```bash
source _path_to_virtual_env_/bin/activate
```
4. download dependencies
```bash
pip install -r requirements.txt
```
5. export flask env
```bash
export FLASK_ENV=development
```
6. export flask app
```bash
export FLASK_APP=wsgi.py
```
7. export flask cert (this ssl certification is only suitable for testing)
```bash
export FLASK_RUN_CERT=adhoc
```
8. export local postgres database
```bash
export DATABASE_URL=_your_database_here_
```
9. have the secrets.py file in the outermost layer of the directory
10. run the app
```bash
flask run
```

## General info
This web application is built with a Flask backend using the App Factory pattern.
It's deployed to Heroku and uses a Heroku PostgreSQL database.  
It uses the default Jinja2 templating engine along with HTML and CSS for the frontend.  

## App directory
The starting point of the app is in wsgi.py. 
The dependencies are given in requirements.txt.
The Python version is given in runtime.txt.
The commands necessary for Heroku are given in Procfile.


App related content is inside the application folder.
The files roughly follow a Model-View-Controller pattern.  
The _models_ folder contains database-related code and class implementations.  
The _templates_ folder contains everything the user sees and related code.  
The _controllers_ folder contains URL routing and form handling.

## Website structure
There are two Flask Blueprints for each of the main sections of the website.
More details of each blueprint are given in the URL section of the wiki.
