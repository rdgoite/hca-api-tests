import time
from collections import deque

from common.auth0 import Authenticator


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

    def clear(self):

        if len(self._queue) > 0:
            self._queue.clear()


class CoreClient:

    def __init__(self, client):
        self._client = client
        self._authenticator = Authenticator()

    def create_submission(self) -> Resource:
        headers = {'Authorization': f'Bearer {self._authenticator.get_token()}'}
        response = self._client.post('/submissionEnvelopes', headers=headers, json={},
                                     name='create new submission')
        response_json = response.json()
        links = response_json.get('_links')
        submission = None
        if links:
            submission = Resource(links)
        return submission
