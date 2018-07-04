from unittest import TestCase

import requests

from config import secrets

AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'
BASE_API_URL = 'http://api.ingest.dev.data.humancellatlas.org'


class AnalysisFileReferenceTest(TestCase):

    def test_no_duplication(self):
        access_token = self._sign_on()
        processes_links = self._prepare_submission(access_token)

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
        links = response.json()['_links']
        self.assertTrue(links, 'Links expected from API response.')
        processes_links = links['processes']
        self.assertTrue(processes_links, 'Link to Process resource expected from API response.')
        return processes_links
