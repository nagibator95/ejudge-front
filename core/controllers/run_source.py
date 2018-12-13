import io

from flask import send_file
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from core.models.base import db
from core.models.run import Run


class RunSourceApi(MethodView):
    def get(self, run_id: int, **___):

        run = db.session.query(Run).get(run_id)

        if run is None:
            raise NotFound(f'Run with id #{run_id} is not found')

        source = run.source

        # TODO: Придумать что-то получше для бинарных submission-ов
        return send_file(io.BytesIO(source),
                         attachment_filename='submission.txt')
