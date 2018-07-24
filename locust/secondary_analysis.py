import json
import os
import re
from configparser import ConfigParser

import requests
from locust import TaskSet, HttpLocust, task

AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
FILE_DIRECTORY = f'{BASE_DIRECTORY}/files/secondary_analysis'

_config = ConfigParser()
_secret_file_path = os.path.join(BASE_DIRECTORY, 'secrets.ini')
_config.read(_secret_file_path)


def secret_default(secret):
    return _config.get('default', secret, fallback=None)


class Submission(object):

    _links = None

    def __init__(self, links):
        self._links = links

    def get_link(self, path):
        return self._links[path]['href']

class SecondarySubmission(TaskSet):

    _url_pattern = None

    _access_token = None

    def on_start(self):
        pattern = f'{self.client.base_url}(?P<url>/.*)'
        self._url_pattern = re.compile(pattern)
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

    @task
    def execute(self):
        submission = self._create_submission()
        processes_link = submission.get_link('processes')
        self._add_analysis_to_submission(processes_link)

    def _create_submission(self):
        headers = {'Authorization': f'Bearer {self._access_token}'}
        response = self.client.post('/submissionEnvelopes', headers=headers, json={})
        response_json = response.json()
        print(json.dumps(response_json, indent=4))
        return Submission(response_json['_links'])

    @staticmethod
    def _add_analysis_to_submission(processes_link):
        with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
            request_json = json.load(analysis_file)
            response = requests.post(processes_link, json=request_json)


class GreenBox(HttpLocust):
    task_set = SecondarySubmission
