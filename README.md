# WCI-Walks
Walkathon web app  
Read the Wiki for specifics

Run locally for testing:  
1. clone repo  
2. create a python3 virtual environment (python3 -m venv venv)  
3. activate the venv (source venv/bin/activate)
4. download dependencies (pip install -r requirements.txt)
5. set up flask env (export FLASK_ENV=development)
6. set up flask app (export FLASK_APP=wsgi.py)
7. set up flask cert (for testing) (export FLASK_RUN_CERT=adhoc)
8. set up a local postgres database (export DATABASE_URL=_your database here_)
9. run (flask run)

URL:
https://wciwalks.herokuapp.com

Version 1.0.0
