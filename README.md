# WCI Walks
![Build Status](https://travis-ci.com/WCI-Computer-Science/WCI-Walks.svg?branch=main "Build Status")

This project will no longer be supported on July 2nd, 2023.

This project is currently maintained by **[@scott-22](https://github.com/scott-22)** and **[@awenelo](https://github.com/awenelo)**.

To take over support of this project please:
1. Fork this GitHub repository
2. Open your fork
3. In the `README.md` file, change the usernames above to be your username and anyone you are working with
4. In the `README.md` file, change the date above to July 2nd the year you are graduating
5. In the `configs.py` file, change the variable EOS_DATE to be `datetime(<year>, 7, 1)`, where `<year>` is the year you're graduating
6. In the `application/templates/contact.html` file, change the names and email address in the urgently contact us section to you and anyone you're working with's emails and names
7. Submit a pull request to merge your fork into this repository - A sample pull request and fork can be found in [#26](https://github.com/WCI-Computer-Science/WCI-Walks/pull/26)

## About this app
WCI Walks tracks the walkathon progress of students at WCI. It tracks individual as well as total progress.

Each student can sign up for an account, and then log in.
Once logged in, they can access user-specific information. This includes the distance they walked on different days, whether they're on the leaderboard, personal statistics, etc. They have two options to log their distances: downloading the Google Fit app and signing in with their account (recommended), or manually inputting distances.

Basic information is displayed on the main page. This includes a leaderboard ranking the people who have walked the most all-time, as well as for the previous day.

As of the time of writing, you can access the app on this URL: https://wciwalks.herokuapp.com.  

Colour scheme:
Main colour: #706c74
Accent color: #746444

## Contributing
Detailed instructions on setting up a development environment to test the app locally are given below.

First, ensure you have PostgreSQL installed and have a database set up.
Then ensure you have created a file called secrets.py with the following variables declared:
```python
secret_key = # Put your secure code for signing cookies
google_client_id = # Put the Client ID of your Google Oauth web application
google_client_secret = # Put the Client Secret of your Google Oauth web application
database_url = # Put the url to connect to your database here
```

After that, follow the instructions below.

1. clone repo to your device
2. have the secrets.py file in the outermost layer of the directory
3. create a python3 virtual environment
```
python3 -m venv _path_to_virtual_env_
```
4. activate the virtual environment
```
source _path_to_virtual_env_/bin/activate
```
5. download dependencies
```
pip install -r requirements.txt
```
6. export flask env
```
export FLASK_ENV=development
```
7. export flask app
```
export FLASK_APP=wsgi.py
```
8. export flask cert (this ssl certification is only suitable for testing)
```
export FLASK_RUN_CERT=adhoc
```
9. run the app
```
flask run
```

## Technical info
This web application is built with a Flask backend and Jinja2/HTML/CSS frontend.  
It's deployed to Heroku and uses a Heroku PostgreSQL database add-on.  
It connects with Google's Fit API to automatically log distances.  

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
There are three Flask Blueprints for each of the main sections of the website.
More details of each blueprint are given in the URL section of the wiki.
