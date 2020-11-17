import json

from flask import g, current_app, request
import requests
from oauthlib.oauth2 import WebApplicationClient
from google.oauth2 import id_token
from google.auth.transport import requests

def get_google_configs():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

def get_client():
    if 'client' not in g:
        g.client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    return g.client

def get_access_token(auth_code):
    client = get_client()
    token_url, headers, body = client.prepare_token_request(
        get_google_configs()['token_endpoint'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=auth_code
    )
    return requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    ).json()['access_token']

def verify_access_token(access_token):
    return id_token.verify_oauth2_token(
        access_token,
        requests.Request(),
        current_app.config['GOOGLE_CLIENT_ID']
    )
