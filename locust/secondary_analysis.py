import json
import os
import time
from collections import deque
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


class Resource(object):

    _links = None

    def __init__(self, links):
        self._links = links

    def get_link(self, path):
        return self._links[path]['href']


class ResourceQueue:

    _queue = deque()

    def queue(self, resource: Resource):
        self._queue.append(resource)

    def wait_for_resource(self):
        submission = self._queue.popleft() if len(self._queue) > 0 else None
        while not submission:
            time.sleep(0.5)
            submission = self._queue.popleft() if len(self._queue) > 0 else None
        return submission


_submission_queue = ResourceQueue()
_analysis_queue = ResourceQueue()


class SecondarySubmission(TaskSet):

    _access_token = None

    _dummy_analysis_details = None

    def on_start(self):
        with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
            self._dummy_analysis_details = json.load(analysis_file)
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
    def setup_analysis(self):
        submission = self._create_submission()
        processes_link = submission.get_link('processes')
        self._add_analysis_to_submission(processes_link)

    def _create_submission(self) -> Resource:
        headers = {'Authorization': f'Bearer {self._access_token}'}
        response = self.client.post('/submissionEnvelopes', headers=headers, json={})
        response_json = response.json()
        submission = Resource(response_json['_links'])
        _submission_queue.queue(submission)
        return submission

    def _add_analysis_to_submission(self, processes_link):
        response = self.client.post(processes_link, json=self._dummy_analysis_details,
                                    name='/submissionEnvelopes/[id]/processes')
        analysis_json = response.json()
        _analysis_queue.queue(Resource(analysis_json['_links']))


class FileStaging(TaskSet):

    _dummy_staging_area_details = None

    def on_start(self):
        with open(f'{FILE_DIRECTORY}/staging_area_patch.json') as patch_file:
            self._dummy_staging_area_details = json.load(patch_file)

    @task
    def update_staging_details(self):
        submission = _submission_queue.wait_for_resource()
        submission_link = submission.get_link('self')
        self.client.put(submission_link, json=self._dummy_staging_area_details,
                        name="/submissionEnvelopes/[id]")


class Validation(TaskSet):

    @task
    def validate_analysis(self):
        analysis = _analysis_queue.wait_for_resource()
        analysis_link = f"{analysis.get_link('self')}"
        self.client.patch(analysis_link, json={'validationErrors': []}, name='/processes/[id]')
        self.client.patch(analysis_link, json={'validationState': 'VALID'}, name='/processes/[id]')


class GreenBox(HttpLocust):
    task_set = SecondarySubmission


class StagingManager(HttpLocust):
    task_set = FileStaging


class Validator(HttpLocust):
    task_set = Validation
