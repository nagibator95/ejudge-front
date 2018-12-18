from datetime import datetime, timedelta
import uuid

from flask import url_for

from core.models import db
from core.models import Run
from core.tests.base import TestCase


class TestTrustedProblemSubmit(TestCase):
    def setUp(self):
        super().setUp()
        self.uuids = [uuid.uuid4().hex for _ in range(3)]

        self.problem_identities = [uuid.uuid4().hex for _ in range(3)]
        self.create_problems(self.problem_identities)

        self.contexts = [uuid.uuid4().hex for _ in range(3)]


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
        self.run4 = Run(user_identity=self.uuids[1], problem_id=self.problems[1].id,
                        ejudge_status=2, ejudge_language_id=2)

        self.run4.create_time = datetime.utcnow() - timedelta(days=1)

        self.run5 = Run(user_identity=self.uuids[1], problem_id=self.problems[0].id,
                        context_identity=self.contexts[0],
                        ejudge_status=2, ejudge_language_id=2)

        db.session.add_all([self.run1, self.run2, self.run3, self.run4, self.run5])

        db.session.commit()

    def send_request(self, problem: str, context_identity=None, **kwargs):
        if context_identity is None:
            url = url_for('problem.problem_runs', problem_identity=problem)
        else:
            url = url_for('problem.problem_context_runs',
                          problem_identity=problem,
                          context_identity=context_identity)
        data = {
            'page': 1,
            **kwargs
        }
        response = self.client.get(url, data=data)
        return response

    def test_simple(self):
        resp = self.send_request(self.problem_identities[0])

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 2)

        self.assertIn('metadata', data['data'])

        self.assertIn('count', data['data']['metadata'])
        self.assertEqual(data['data']['metadata']['count'], 2)

        self.assertIn('page_count', data['data']['metadata'])
        self.assertEqual(data['data']['metadata']['page_count'], 1)

        run0 = data['data']['runs'][0]

        # Common fields
        self.assertIn('id', run0)
        self.assertIsNotNone(run0['id'])

        self.assertIn('user_identity', run0)
        self.assertIsNotNone(run0['user_identity'])

        self.assertIn('problem_identity', run0)
        self.assertIsNotNone(run0['problem_identity'])

        self.assertIn('ejudge_status', run0)
        self.assertIsNotNone(run0['ejudge_status'])

        self.assertIn('create_time', run0)
        self.assertIsNotNone(run0['create_time'])

        self.assertIn('language_id', run0)
        self.assertIn('ejudge_last_change_time', run0)

    def test_filter_by_user(self):
        resp = self.send_request(self.problem_identities[0], uid=self.uuids[0])

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 1)

    def test_filter_by_lang(self):
        resp = self.send_request(self.problem_identities[0], lang_id=self.run1.ejudge_language_id)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 1)

    def test_filter_by_status(self):
        resp = self.send_request(self.problem_identities[0], status_id=self.run1.ejudge_status)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 1)

    def test_filter_by_context(self):
        resp = self.send_request(self.problem_identities[0],
                                 context_identity=self.contexts[0])

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 1)

    def test_filter_by_from_timestamp(self):

        from_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)

        resp = self.send_request(self.problem_identities[1], from_timestamp=from_time)

        self.assert200(resp)

        data = resp.get_json()

        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 1)

        # Too mush for timestamp
        resp = self.send_request(self.problem_identities[1], from_timestamp=from_time * 10000)
        self.assert400(resp)

    def test_filter_by_to_timestamp(self):

        to_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)

        resp = self.send_request(self.problem_identities[1], to_timestamp=to_time)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['runs']), 1)

        # Too mush for timestamp
        resp = self.send_request(self.problem_identities[1], to_timestamp=to_time * 10000)
        self.assert400(resp)
