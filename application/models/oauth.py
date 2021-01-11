import json

import google.auth.transport.requests
import requests
from flask import current_app, g, request
from google.oauth2 import id_token
from oauthlib.oauth2 import WebApplicationClient


def get_google_configs():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

def get_client():
    if 'client' not in g:
        g.client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    return g.client

def get_id_token(auth_code):
    client = get_client()
    token_url, headers, body = client.prepare_token_request(
        get_google_configs()['token_endpoint'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=auth_code,
        hd='wrdsb.ca'
    )
    return requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    ).json()['id_token']

def verify_id_token(token):
    return id_token.verify_oauth2_token(
        token,
        google.auth.transport.requests.Request(),
        current_app.config['GOOGLE_CLIENT_ID']
    )
