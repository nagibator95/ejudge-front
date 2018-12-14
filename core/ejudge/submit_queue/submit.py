import logging
from flask import current_app

from core.ejudge.ejudge_proxy import submit
from core.models import db
from core.models.run import Run
from core.utils.helpers import attrs_to_dict


log = logging.getLogger('submit_queue')


def ejudge_error_notification(ejudge_response=None):
    code = None
    message = 'Ошибка отправки задачи'
    try:
        code = ejudge_response['code']
        message = ejudge_response['message']
    except Exception:
        pass
    return {
        'ejudge_error': {
            'code': code,
            'message': message,
        }
    }


class Submit:
    def __init__(self, id, user_id, run_id: int, ejudge_url: str):
        self.id = id
        self.user_id = user_id
        self.run_id = run_id
        self.ejudge_url = ejudge_url
        self.ejudge_user = current_app.config.get('EJUDGE_USER')
        self.ejudge_password = current_app.config.get('EJUDGE_PASSWORD')

    def send(self, ejudge_url=None):

        ejudge_url = ejudge_url or self.ejudge_url

        run = db.session.query(Run).get(self.run_id)
        if not run:
            log.error(f'Can\'t find run #{self.run_id}')
            return
        file = run.source
        problem = run.problem
        ejudge_language_id = run.ejudge_language_id
        user_id = run.user_id

        # `Run` now not inside the submit_queue so we should change status
        run.status = 98  # Compiling
        db.session.add(run)
        db.session.commit()

        try:
            ejudge_response = submit(
                run_file=file,
                contest_id=problem.ejudge_contest_id,
                prob_id=problem.problem_id,
                lang_id=ejudge_language_id,
                login=self.ejudge_user,
                password=self.ejudge_password,
                filename='common_filename',
                url=ejudge_url,
                user_id=user_id
            )
        except Exception:
            log.exception('Unknown Ejudge submit error')
            return

        try:
            if ejudge_response['code'] != 0:
                return

            ejudge_run_id = ejudge_response['run_id']
        except Exception:
            log.exception('ejudge_proxy.submit returned bad value')
            return

        run.ejudge_run_id = ejudge_run_id
        run.ejudge_url = ejudge_url

        db.session.add(run)
        db.session.commit()

        db.session.refresh(run)

    def encode(self):
        return {
            'id': self.id,
            'run_id': self.run_id,
            'ejudge_url': self.ejudge_url,
            'user_id': self.user_id,
        }

    @staticmethod
    def decode(encoded):
        return Submit(
            id=encoded['id'],
            run_id=encoded['run_id'],
            ejudge_url=encoded['ejudge_url'],
            user_id=encoded['user_id'],
        )

    def serialize(self, attributes=None):
        if attributes is None:
            attributes = (
                'id',
            )
        serialized = attrs_to_dict(self, *attributes)
        return serialized
