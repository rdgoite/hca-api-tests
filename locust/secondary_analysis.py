import json
import os
import re
import time
from collections import deque
from configparser import ConfigParser

import logging
import requests
from locust import TaskSet, HttpLocust, task, seq_task

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


class SubmissionQueue:

    _queue = deque()

    def queue(self, submission: Submission):
        self._queue.append(submission)

    def wait_for_submission(self):
        submission = self._queue.popleft() if len(self._queue) > 0 else None
        while not submission:
            time.sleep(0.5)
            submission = self._queue.popleft() if len(self._queue) > 0 else None
        return submission


_submission_queue = SubmissionQueue()


class SecondarySubmission(TaskSet):

    _url_pattern = None

    _access_token = None

    _submission = None

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

    @seq_task(1)
    def setup_analysis(self):
        submission = self._create_submission()
        processes_link = submission.get_link('processes')
        self._add_analysis_to_submission(processes_link)

    def _create_submission(self) -> Submission:
        headers = {'Authorization': f'Bearer {self._access_token}'}
        response = self.client.post('/submissionEnvelopes', headers=headers, json={})
        response_json = response.json()
        submission = Submission(response_json['_links'])
        _submission_queue.queue(submission)
        return submission

    @staticmethod
    def _add_analysis_to_submission(processes_link):
        with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
            request_json = json.load(analysis_file)
            requests.post(processes_link, json=request_json)

    @seq_task(2)
    def upload_files(self):
        submission = _submission_queue.wait_for_submission()
        submission_link = submission.get_link('self')
        staging_area_url = self._get_staging_area_url(submission_link)
        while not staging_area_url:
            time.sleep(2)
            logging.debug(f'Reattempting to retrieve staging details from [{submission_link}]...')
            staging_area_url = self._get_staging_area_url(submission_link)
        logging.info(f'Retrieved staging details from [{submission_link}].')

    @staticmethod
    def _get_staging_area_url(submission_link):
        url = None
        response = requests.get(submission_link).json()
        staging_details = response.get('stagingDetails')
        if staging_details:
            url = staging_details['stagingAreaLocation']['value']
        return url


class GreenBox(HttpLocust):
    task_set = SecondarySubmission
