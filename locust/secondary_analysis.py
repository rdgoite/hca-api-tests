import json
import os
import time
from collections import deque
from configparser import ConfigParser

import copy
import requests
from locust import TaskSet, HttpLocust, task

AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
FILE_DIRECTORY = f'{BASE_DIRECTORY}/files/secondary_analysis'

DEFAULT_FILE_UPLOAD_URL = 'http://localhost:8888/v1'

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

with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
    _dummy_analysis = json.load(analysis_file)
    
with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
    _dummy_analysis = json.load(analysis_file)

_analysis_file_template = {
    'fileName': '',
    'content': {
        'lane': 1,
        'type': 'reads',
        'name': '',
        'format': '.fastq.gz'
    }
}

_dummy_analysis_files = []
for name in ['ERR1630013.fastq.gz', 'ERR1630014.fastq.gz']:
    test_file = copy.copy(_analysis_file_template)
    test_file['fileName'] = name
    test_file['content']['name'] = name
    _dummy_analysis_files.append(test_file)


_file_upload_base_url = os.environ.get('FILE_UPLOAD_URL')
if not _file_upload_base_url:
    _file_upload_base_url = DEFAULT_FILE_UPLOAD_URL


class SecondarySubmission(TaskSet):

    _access_token = None

    def on_start(self):
        self._access_token = secret_default('access_token')

    @task
    def setup_analysis(self):
        submission = self._create_submission()
        if submission:
            self._add_analysis_to_submission(submission)

    def _create_submission(self) -> Resource:
        headers = {'Authorization': f'Bearer {self._access_token}'}
        response = self.client.post('/submissionEnvelopes', headers=headers, json={},
                                    name='create new submission')
        response_json = response.json()
        links = response_json.get('_links')
        submission = None
        if links:
            submission = Resource(links)
            _submission_queue.queue(submission)
        return submission

    def _add_analysis_to_submission(self, submission: Resource):
        processes_link = submission.get_link('processes')
        response = self.client.post(processes_link, json=_dummy_analysis,
                                    name='add analysis to submission')
        analysis_json = response.json()
        links = analysis_json.get('_links')
        if links:
            analysis = Resource(links)
            _analysis_queue.queue(analysis)
            self._add_file_reference(analysis)
            self._upload_files(submission)

    def _add_file_reference(self, analysis: Resource):
        file_reference_link = analysis.get_link('add-file-reference')
        for dummy_analysis_file in _dummy_analysis_files:
            self.client.put(file_reference_link, json=dummy_analysis_file,
                            name="add file reference")

    def _upload_files(self, submission: Resource):
        upload_area_uuid = None
        submission_link = submission.get_link('self')
        while not upload_area_uuid:
            upload_area_uuid = self._get_upload_area_uuid(submission_link)
        for _dummy_analysis_file in _dummy_analysis_files:
            upload_url = f'{_file_upload_base_url}/area/{upload_area_uuid}/files'
            file_json = {'fileName': _dummy_analysis_file['fileName'], 'contentType': 'fastq'}
            requests.put(upload_url, json=file_json)

    def _get_upload_area_uuid(self, submission_link):
        upload_area_uuid = None
        submission_data = self.client.get(submission_link, name='get submission data').json()
        staging_details = submission_data.get('stagingDetails')
        if staging_details:
            staging_area_uuid = staging_details.get('stagingAreaUuid')
            if staging_area_uuid:
                upload_area_uuid = staging_area_uuid.get('uuid')
        return upload_area_uuid


class GreenBox(HttpLocust):
    task_set = SecondarySubmission
