import copy
import json
import os
import sys
import time

import logging
import requests
from locust import TaskSet, HttpLocust, task

# sys.path setup needs to happen before import of common module
sys.path.append(os.getcwd())

from common.auth0 import Authenticator
from locust.core_client import CoreClient, Resource, ResourceQueue

DEFAULT_FILE_UPLOAD_URL = 'http://localhost:8888/v1'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
FILE_DIRECTORY = f'{BASE_DIRECTORY}/files/secondary_analysis'

_submission_queue = ResourceQueue()
_analysis_queue = ResourceQueue()

with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
    _dummy_analysis = json.load(analysis_file)
    
with open(f'{FILE_DIRECTORY}/analysis.json') as analysis_file:
    _dummy_analysis = json.load(analysis_file)

_file_template = {
    'fileName': '',
    'content': {
        'describedBy': 'https://schema.humancellatlas.org/type/file/6.1.1/sequence_file',
        'schema_type': 'file',
        'read_index': 'read1',
        'lane_index': 1
    }
}


def _create_test_file(name):
    test_file = copy.copy(_file_template)
    test_file['fileName'] = name
    split = name.split('.', 1)
    format = split[1] if len(split) > 1 else None
    test_file['content']['file_core'] = {'file_name': name, 'file_format': format}
    return test_file


_dummy_analysis_files = []
_base_name = 'ERR16300'
for index in range(1, 31):
    name = f'{_base_name}{"%02d" % index}.fastq.gz'
    _dummy_analysis_files.append(_create_test_file(name))


_file_upload_base_url = os.environ.get('FILE_UPLOAD_URL', DEFAULT_FILE_UPLOAD_URL)


_authenticator = Authenticator()


class SecondarySubmission(TaskSet):

    _core_client = None

    def on_start(self):
        self._core_client = CoreClient(self.client)

    def on_stop(self):
        _authenticator.end_session()
        _submission_queue.clear()
        _analysis_queue.clear()

    @task
    def setup_analysis(self):
        submission = self._core_client.create_submission()
        if submission:
            _submission_queue.queue(submission)
            self._add_analysis_to_submission(submission)

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
        upload_url = f'{_file_upload_base_url}/area/{upload_area_uuid}/files'
        logging.info(f'uploading dummy files to [{upload_url}]...')
        for _dummy_analysis_file in _dummy_analysis_files:
            file_json = {
                'fileName': _dummy_analysis_file['fileName'],
                'contentType': 'application/tar+gzip;dcp-type=data'
            }
            requests.put(upload_url, json=file_json)


class GreenBox(HttpLocust):
    task_set = SecondarySubmission

    def setup(self):
        pass

    def _setup_input_bundle(self):
        pass


class FileUploader(HttpLocust):
    task_set = FileUpload
