from locust import TaskSet, task, HttpLocust

from common.auth0 import Authenticator
from common.core_client import CoreClient, Resource


class TestSubmission(TaskSet):

    _authenticator = Authenticator()
    _submission: Resource = None

    def on_start(self):
        core_client = CoreClient(self.client)
        self._submission = core_client.create_submission(self._authenticator.get_token())

    def on_stop(self):
        self._authenticator.end_session()

    @task
    def get_submission(self):
        submission_link = self._submission.get_link('self')
        self.client.get(submission_link)


class Submitter(HttpLocust):
    task_set = TestSubmission
