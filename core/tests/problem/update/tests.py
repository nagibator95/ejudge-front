import json
import uuid

from flask import url_for

from core.models import db
from core.models import Problem
from core.tests.base import TestCase


class TestGetSubmissionSource(TestCase):
    def setUp(self):
        super().setUp()

        problem_identity = uuid.uuid4().hex
        self.problem = Problem(problem_identity=problem_identity,
                               ejudge_problem_id=1,
                               ejudge_contest_id=2)
        db.session.add(self.problem)
        db.session.commit()

    def send_request(self, data, problem_identity=None):
        problem_identity = problem_identity or self.problem.problem_identity

        url = url_for('problem.problem_by_identity',
                      problem_identity=problem_identity)
        data = json.dumps(data)

        resp = self.client.put(url, data=data)

        print(resp.json)

        return resp

    def test_simple(self):
        data = {
            'problem': {
                'ejudge_contest_id': 2,
                'ejudge_problem_id': '2',
            }
        }
        resp = self.send_request(data)
        self.assertStatus(resp, 200)

        problem = db.session.query(Problem).\
            filter(Problem.problem_identity == self.problem.problem_identity).\
            one_or_none()

        self.assertEqual(problem.ejudge_contest_id, 2)
        self.assertEqual(problem.ejudge_problem_id, 2)

        self.assertIn('data', resp.json)

        data = resp.json['data']

        self.assertIn('problem_identity', data)

        self.assertEqual(data['problem_identity'], problem.problem_identity)

    def test_partial(self):
        data = {
            'problem': {
                'ejudge_problem_id': 1,
            }
        }
        resp = self.send_request(data)
        self.assert200(resp)

        problem = db.session.query(Problem). \
            filter(Problem.problem_identity == self.problem.problem_identity). \
            one_or_none()

        self.assertEqual(problem.ejudge_problem_id, 1)

    def test_wrong(self):
        data = {
            'not_a_prob': {
                'ejudge_contest_id': 4,
                'ejudge_problem_id': 4,
            }
        }

        resp = self.send_request(data)
        self.assert400(resp)

        data = {
            'problem': {
                'ejudge_contest_id': 'not an int',
                'ejudge_problem_id': 4,
            }
        }

        resp = self.send_request(data)
        self.assert400(resp)

    def test_wrong_identity(self):
        data = {
            'problem': {
                'ejudge_contest_id': 4,
                'ejudge_problem_id': 4,
            }
        }

        resp = self.send_request(data, problem_identity='Undefined problem')
        self.assert404(resp)

    def test_try_to_change_identity(self):
        data = {
            'problem': {
                'problem_identity': 'my new identity',
                'ejudge_contest_id': 4,
                'ejudge_problem_id': 4,
            }
        }
        resp = self.send_request(data)
        self.assertStatus(resp, 200)

        problem = db.session.query(Problem). \
            filter(Problem.problem_identity == self.problem.problem_identity). \
            one_or_none()

        self.assertEqual(problem.problem_identity, self.problem.problem_identity)
        self.assertEqual(problem.ejudge_problem_id, 4)
