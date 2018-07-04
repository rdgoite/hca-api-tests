from unittest import TestCase

import requests

from config import secrets

AUTH_BROKER_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'


class AnalysisFileReferenceTest(TestCase):

    def test_no_duplication(self):
        # given:
        request_body = {
            'client_id': secrets.get_default('client_id'),
            'client_secret': secrets.get_default('client_secret'),
            'audience': 'http://localhost:8080',
            'grant_type': 'client_credentials'
        }

        # and: assume
        self.assertIsNotNone(request_body.get('client_id'), 'client_id must be set.')
        self.assertIsNotNone(request_body.get('client_secret', 'client_secret must be set.'))

        # when:
        response = requests.post(AUTH_BROKER_URL, json=request_body)
        response_json = response.json()

        self.assertIsNotNone(response_json['access_token'])
