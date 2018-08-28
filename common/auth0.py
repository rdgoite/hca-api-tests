import os

import logging
import requests

DEFAULT_AUTH0_DOMAIN = 'danielvaughan.eu.auth0.com'

_auth_broker_url = os.environ.get('AUTH0_DOMAIN', DEFAULT_AUTH0_DOMAIN)
_auth_broker_url = f'https://{_auth_broker_url}/oauth/token'

_client_id = os.environ.get('CLIENT_ID', '')
_client_secret = os.environ.get('CLIENT_SECRET', '')

_sign_on_request = {
    'client_id': _client_id,
    'client_secret': _client_secret,
    'audience': 'http://localhost:8080',
    'grant_type': 'client_credentials'
}


def sign_on():
    response = requests.post(_auth_broker_url, json=_sign_on_request)
    return response.json()['access_token']


class Authenticator:

    def __init__(self):
        self._access_token = None

    def start_session(self):
        logging.info('Starting auth session...')
        self._access_token = sign_on()

    def get_token(self):
        if not self._access_token:
            self.start_session()
        return self._access_token

    def end_session(self):
        if self._access_token:
            logging.info('Stopping auth session...')
            self._access_token = None
