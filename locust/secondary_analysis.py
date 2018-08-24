import copy
import json
import os
import time
from collections import deque

import requests
from locust import TaskSet, HttpLocust, task

DEFAULT_AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'
DEFAULT_FILE_UPLOAD_URL = 'http://localhost:8888/v1'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
FILE_DIRECTORY = f'{BASE_DIRECTORY}/files/secondary_analysis'

class Resource(object):

    _links = None

    def __init__(self, links):
        self._links = links

    def get_link(self, path):
        return self._links[path]['href']


class ResourceQueue:

    def __init__(self):
        self._queue = deque()

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
    test_file['content'] = {
        'describedBy': 'https://schema.humancellatlas.org/type/file/6.1.1/sequence_file',
        'name': name
    }
    _dummy_analysis_files.append(test_file)


_file_upload_base_url = os.environ.get('FILE_UPLOAD_URL', DEFAULT_FILE_UPLOAD_URL)

_auth_broker_url = os.environ.get('AUTH_BROKER_URL', DEFAULT_AUTH_BROKER_URL)
_client_id = os.environ.get('CLIENT_ID', '')
_client_secret = os.environ.get('CLIENT_SECRET', '')

_sign_on_request = {
    'client_id': _client_id,
    'client_secret': _client_secret,
    'audience': 'http://localhost:8080',
    'grant_type': 'client_credentials'
}


def _sign_on():
    global _access_token
    response = requests.post(DEFAULT_AUTH_BROKER_URL, json=_sign_on_request)
    _access_token = response.json()['access_token']


_sign_on()


class SecondarySubmission(TaskSet):

    def on_start(self):
        pass

    @task
    def setup_analysis(self):
        submission = self._create_submission()
        if submission:
            self._add_analysis_to_submission(submission)

    def _create_submission(self) -> Resource:
        headers = {'Authorization': f'Bearer {_access_token}'}
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

    def _add_file_reference(self, analysis: Resource):
        file_reference_link = analysis.get_link('add-file-reference')
        for dummy_analysis_file in _dummy_analysis_files:
            self.client.put(file_reference_link, json=dummy_analysis_file,
                            name="add file reference")


class FileUpload(TaskSet):

    def on_start(self):
        pass

    @task
    def upload_files(self):
        submission = _submission_queue.wait_for_resource()
        upload_area_uuid = None
        submission_link = submission.get_link('self')
        while not upload_area_uuid:
            upload_area_uuid = self._get_upload_area_uuid(submission_link)
            if not upload_area_uuid:
                time.sleep(3)
        FileUpload._upload_dummy_files(upload_area_uuid)

    def _get_upload_area_uuid(self, submission_link):
        upload_area_uuid = None
        submission_data = self.client.get(submission_link, name='get submission data').json()
        staging_details = submission_data.get('stagingDetails')
        if staging_details:
            staging_area_uuid = staging_details.get('stagingAreaUuid')
            if staging_area_uuid:
                upload_area_uuid = staging_area_uuid.get('uuid')
        return upload_area_uuid

    @staticmethod
    def _upload_dummy_files(upload_area_uuid):
        print('uploading dummy files...')
        for _dummy_analysis_file in _dummy_analysis_files:
            upload_url = f'{_file_upload_base_url}/area/{upload_area_uuid}/files'
            file_json = {
                'fileName': _dummy_analysis_file['fileName'],
                'contentType': 'application/tar+gzip;dcp-type=data'
            }
            requests.put(upload_url, json=file_json)


class GreenBox(HttpLocust):
    task_set = SecondarySubmission


class FileUploader(HttpLocust):
    task_set = FileUpload
