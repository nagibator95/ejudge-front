import json

from flask import url_for

from core.models import db
from core.models import Problem
from core.tests.base import TestCase


class TestGetSubmissionSource(TestCase):
    def setUp(self):
        super().setUp()

    def send_request(self, data):
        url = url_for('problem.problem')

        data = json.dumps(data)

        resp = self.client.post(url, data=data)

        print(resp.json)

        return resp

    def test_simple(self):
        data = {
            'problem': {
                'ejudge_contest_id': 1,
                'ejudge_problem_id': '1',
            }
        }
        resp = self.send_request(data)

        self.assertStatus(resp, 201)

        problems = db.session.query(Problem).all()

        self.assertEqual(len(problems), 1)

        problem = problems[0]

        self.assertEqual(problem.ejudge_contest_id, 1)
        self.assertEqual(problem.ejudge_problem_id, 1)

        self.assertIn('data', resp.json)

        data = resp.json['data']

        self.assertIn('problem_identity', data)

        self.assertEqual(data['problem_identity'], problem.problem_identity)

    def test_wrong_data(self):
        data = {
            'problem': {
                'ejudge_contest_id': 'this is not int!',
                'ejudge_problem_id': 1,
            }
        }
        resp = self.send_request(data)
        self.assert400(resp)

        data = {
            'not_a_problem': {
                'ejudge_contest_id': 1,
                'ejudge_problem_id': 1,
            }
        }

        resp = self.send_request(data)
        self.assert400(resp)
