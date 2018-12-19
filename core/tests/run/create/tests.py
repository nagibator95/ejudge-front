import io
from io import BytesIO
import uuid
from unittest.mock import MagicMock, patch

from flask import url_for

from core.controllers.run import ProblemRunApi
from core.tests.base import TestCase
from core.models import db, Run


class TestCheckFileRestriction(TestCase):
    def setUp(self):
        super().setUp()

    def test_file_too_large(self):
        files = io.BytesIO(bytes((ascii('f') * 64 * 1024).encode('ascii')))
        with self.assertRaises(ValueError):
            ProblemRunApi._check_file_restriction(files)

        files = io.BytesIO(bytes((ascii('f') * 1).encode('ascii')))

        with self.assertRaises(ValueError):
            ProblemRunApi._check_file_restriction(files)


class TestProblemSubmitCreation(TestCase):
    def setUp(self):
        super().setUp()
        self.uuids = [uuid.uuid4().hex for _ in range(3)]

        self.problem_identities = [uuid.uuid4().hex for _ in range(3)]
        self.create_problems(self.problem_identities)

        self.contexts = [uuid.uuid4().hex for _ in range(3)]

    def send_request(self, problem: str, context_identity=None, **kwargs):
        if context_identity is None:
            url = url_for('problem.problem_runs', problem_identity=problem)
        else:
            url = url_for('problem.problem_context_runs',
                          problem_identity=problem,
                          context_identity=context_identity)
        data = {
            'lang_id': 1,
            'uid': self.uuids[0],
            **kwargs
        }
        response = self.client.post(url, data=data, content_type='multipart/form-data')
        return response

    @patch('core.controllers.run.Run.update_source')
    @patch('core.controllers.run.queue_submit')
    def test_simple(self, mock_submit, mock_update):
        mock_submit.return_value = {'hhh': 'mmm'}

        file = BytesIO(b'skdjvndfkjnvfk')
        data = dict(
            file=(file, 'test.123', ),
        )
        resp = self.send_request(self.problem_identities[0], context_identity=self.contexts[0], **data)

        self.assertStatus(resp, 201)
        mock_update.assert_called_once()
        mock_submit.assert_called_once()

    @patch('core.controllers.run.Run.update_source')
    @patch('core.controllers.run.queue_submit')
    def test_duplicate(self, mock_submit, mock_update):
        submit = MagicMock()
        submit.serialize.return_value = {'hhh': 'mmm'}
        mock_submit.return_value = submit

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)

        run = Run(
            user_identity=self.uuids[0],
            problem=self.problems[0],
            problem_id=self.problems[0].id,
            context_identity=self.contexts[0],
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=1,
            ejudge_status=98,  # compiling
            source_hash=source_hash,
        )
        db.session.add(run)
        db.session.commit()

        file = BytesIO(blob)
        data = dict(
            file=(file, 'test.123', )
        )
        resp = self.send_request(self.problem_identities[0],
                                 context_identity=self.contexts[0],
                                 **data)

        self.assert400(resp)
