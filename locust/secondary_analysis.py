import os
from configparser import ConfigParser

import requests
from locust import TaskSet, seq_task, HttpLocust

AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

_config = ConfigParser()
_secret_file_path = os.path.join(BASE_DIRECTORY, 'secrets.ini')
_config.read(_secret_file_path)


def secret_default(secret):
    return _config.get('default', secret, fallback=None)


class SecondarySubmission(TaskSet):
    _access_token = None

    def on_start(self):
        self.authenticate()

    def authenticate(self):
        auth_request = {
            'client_id': secret_default('client_id'),
            'client_secret': secret_default('client_secret'),
            'audience': 'http://localhost:8080',
            'grant_type': 'client_credentials'
        }
        response = requests.post(AUTH_BROKER_URL, json=auth_request)
        credentials_json = response.json()
        self._access_token = credentials_json.get('access_token')

    @seq_task(1)
    def create_submission(self):
        headers = {'Authorization': f'Bearer {self._access_token}'}
        self.client.post('/submissionEnvelopes', headers=headers, json={})


class GreenBox(HttpLocust):
    task_set = SecondarySubmission
