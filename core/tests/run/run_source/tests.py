import uuid

from flask import url_for

from core import db
from core.models import Run
from core.tests.base import TestCase


class TestGetSubmissionSource(TestCase):
    def setUp(self):
        super().setUp()

        self.uuids = [uuid.uuid4().hex for _ in range(3)]

        self.problem_identities = [uuid.uuid4().hex for _ in range(3)]
        self.create_problems(self.problem_identities)

        self.contexts = [uuid.uuid4().hex for _ in range(3)]

        db.session.flush()

        self.run = Run(user_identity=self.uuids[0], problem_id=self.problems[0].id,
                        ejudge_status=1, ejudge_language_id=1)

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)
        self.run.source_hash = source_hash

        db.session.add(self.run)
        db.session.commit()

        self.run.update_source(blob)

    def send_request(self, run_id):
        url = url_for('problem.problem_runs_update',
                      problem_identity='I_dont_care',
                      run_id=run_id)
        response = self.client.get(url)
        return response

    def test_simple(self):

        resp = self.send_request(run_id=self.run.id)
        self.assert200(resp)
