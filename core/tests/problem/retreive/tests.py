import uuid
from pprint import pprint
from unittest.mock import patch

from flask import url_for

from core.models import db
from core.models import Problem
from core.tests.base import TestCase


class TestGetSubmissionSource(TestCase):
    def setUp(self):
        super().setUp()
        self.problem_identity = uuid.uuid4().hex
        problem = Problem(problem_identity=self.problem_identity,
                          ejudge_contest_id=1,
                          ejudge_problem_id=1)
        db.session.add(problem)
        db.session.commit()

    def send_request(self, problem_identity, data=None):
        data = data or {}
        url = url_for('problem.problem_by_identity',
                      problem_identity=problem_identity, **data)

        resp = self.client.get(url)

        print(resp.json)

        return resp

    def test_not_found(self):
        problem_identity = 'undefinde_prob_uuid'
        resp = self.send_request(problem_identity)
        self.assert404(resp)

    @patch('core.models.problem.Problem.generate_samples_json')
    def test_with_samples(self, generate_samples_mock):
        samples = {'first_sample': 'lfdjbngljb'}
        generate_samples_mock.return_value = samples

        data = {
            'with_fields': ['samples']
        }

        resp = self.send_request(self.problem_identity, data)

        self.assert200(resp)
        self.assertIn('data', resp.json)

        data = resp.json['data']

        self.assertIn('samples', data)
        generate_samples_mock.assert_called_once()
        self.assertEqual(data['samples'], samples)

    @patch('core.models.problem.Problem.generate_samples_json')
    def test_without_samples(self, generate_samples_mock):
        samples = {'first_sample': 'lfdjbngljb'}
        generate_samples_mock.return_value = samples

        data = {
            'with_fields': []
        }

        resp = self.send_request(self.problem_identity, data)

        self.assert200(resp)
        self.assertIn('data', resp.json)

        data = resp.json['data']

        pprint(data)

        self.assertNotIn('samples', data)
        generate_samples_mock.assert_not_called()
