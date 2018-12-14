import json
import uuid

from flask import url_for

from core import db
from core.models import Run
from core.tests.base import TestCase


class TestAPIProblemSubmission(TestCase):
    def setUp(self):
        super().setUp()

        self.uuids = [uuid.uuid4().hex for _ in range(3)]

        self.problem_identities = [uuid.uuid4().hex for _ in range(3)]
        self.create_problems(self.problem_identities)

        self.contexts = [uuid.uuid4().hex for _ in range(3)]

        db.session.flush()

        self.run1 = Run(user_identity=self.uuids[0], problem_id=self.problems[0].id,
                        ejudge_status=1, ejudge_language_id=1)
        self.run2 = Run(user_identity=self.uuids[0], problem_id=self.problems[1].id,
                        ejudge_status=1, ejudge_language_id=1)
        self.run3 = Run(user_identity=self.uuids[1], problem_id=self.problems[0].id,
                        ejudge_status=2, ejudge_language_id=2)

        db.session.add_all([self.run1, self.run2, self.run3])

        db.session.commit()

    def send_request(self, run_id: int, **kwargs):
        url = url_for('problem.problem_runs_update',
                      problem_identity='i_dont_care',
                      run_id=run_id)
        resp = self.client.put(url, data=json.dumps(kwargs))

        return resp

    def test_simple(self):
        run_id = self.run1.id

        data = {
            'run': {
                'ejudge_status': 444,
            }
        }

        resp = self.send_request(run_id, **data)

        self.assert200(resp)

        self.assertIn('data', resp.json)

        data = resp.json['data']

        self.assertIn('id', data)
        self.assertIsNotNone(data['id'])

        self.assertIn('user_identity', data)
        self.assertIsNotNone(data['user_identity'])

        self.assertIn('ejudge_status', data)
        self.assertEqual(data['ejudge_status'], 444)

        self.assertIn('create_time', data)
        self.assertIsNotNone(data['create_time'])

        run = db.session.query(Run).get(run_id)

        self.assertEqual(run.ejudge_status, 444)

    def test_bad_request(self):
        run_id = self.run1.id

        data = {
            'run': {
                'ejudge_status': 'this is not int',
            }
        }

        resp = self.send_request(run_id, **data)

        self.assert400(resp)
