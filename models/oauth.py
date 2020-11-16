from flask import g, current_app
from oauthlib.oauth2 import WebApplicationClient

def get_client():
    if 'client' not in g:
        g.client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    return g.client