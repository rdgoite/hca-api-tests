from unittest import TestCase

import requests

from config import secrets

AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'
BASE_API_URL = 'http://api.ingest.dev.data.humancellatlas.org'


class AnalysisFileReferenceTest(TestCase):

    def test_no_duplication(self):
        access_token = self._sign_on()
        processes_link = self._prepare_submission(access_token)

        analysis_request = {
            'process_core': {
                'process_id': 'test_process_1'
            },
            'schema_type': 'process',
            'describedBy': 'https://schema.humancellatlas.org/type/process/1.0.0/process'
        }
        response = requests.post(processes_link, json=analysis_request)
        links = response.json().get('_links')
        add_file_reference_link = links.get('add-file-reference')
        self.assertTrue(add_file_reference_link, 'Link to adding File reference expected.')
        derived_files_link = links.get('derivedFiles')
        self.assertTrue(derived_files_link, 'Link to get derived Files expected.')
        derived_files_link = derived_files_link.get('href')

        self._assert_resource_count(derived_files_link, 0)

    def _sign_on(self):
        request_body = {
            'client_id': secrets.get_default('client_id'),
            'client_secret': secrets.get_default('client_secret'),
            'audience': 'http://localhost:8080',
            'grant_type': 'client_credentials'
        }
        self.assertIsNotNone(request_body.get('client_id'), 'client_id must be set.')
        self.assertIsNotNone(request_body.get('client_secret', 'client_secret must be set.'))

        response = requests.post(AUTH_BROKER_URL, json=request_body)
        access_token = response.json()['access_token']
        self.assertIsNotNone(access_token, 'Access token expected from auth broker.')
        return access_token

    def _prepare_submission(self, access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_API_URL}/submissionEnvelopes', headers=headers, json={})
        links = response.json().get('_links')
        self.assertTrue(links, 'Links expected from API response.')
        processes_link = links.get('processes')
        self.assertTrue(processes_link, 'Link to Process resource expected from API response.')
        return processes_link.get('href')

    def _assert_resource_count(self, derived_files_link, total_count):
        response = requests.get(derived_files_link)
        page_details = response.json().get('page')
        self.assertEqual(total_count, page_details.get('totalElements'))
