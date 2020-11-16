from flask import g, current_app, requests
from oauthlib.oauth2 import WebApplicationClient

def get_google_configs():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

def get_client():
    if 'client' not in g:
        g.client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    return g.client