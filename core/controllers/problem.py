import datetime

from flask import request, current_app
from flask.views import MethodView
from marshmallow import fields
from webargs.flaskparser import parser
from werkzeug.exceptions import BadRequest, NotFound

from core.controllers.serializers.run import RunSchema
from core.ejudge.submit_queue import queue_submit
from core.models import db, Run, Problem
from core.utils import jsonify

get_args = {
    'uid': fields.List(fields.String()),
    'lang_id': fields.Integer(),
    'status_id': fields.Integer(),
    'count': fields.Integer(default=10, missing=10),
    'page': fields.Integer(required=True),
    'from_timestamp': fields.Integer(),  # Может быть -1, тогда не фильтруем
    'to_timestamp': fields.Integer(),  # Может быть -1, тогда не фильтруем
}

post_args = {
    'lang_id': fields.Integer(required=True),
    'uid': fields.String(required=True),
}


class ProblemRunApi(MethodView):
    def get(self, problem_identity: str, context_identity=None):
        """ View for getting problem submissions

            Possible filters
            ----------------
            from_timestamp: timestamp
            to_timestamp: timestamp
            uid: [str]
            lang_id: int
            status_id: int
            context_identity: str | None

            Returns
            --------
            'result': success | error
            'data': [Run]
            'metadata': {count: int, page_count: int}
        """
        args = parser.parse(get_args, request)
        uids = args.get('uid')
        lang_id = args.get('lang_id')
        status_id = args.get('status_id')
        from_timestamp = args.get('from_timestamp')
        to_timestamp = args.get('to_timestamp')

        per_page_count = args.get('count')
        page = args.get('page')

        try:
            # TODO: убрать деление на тысячу
            from_timestamp = from_timestamp and from_timestamp != -1 and \
                             datetime.datetime.fromtimestamp(from_timestamp / 1_000)
            to_timestamp = to_timestamp and to_timestamp != -1 and \
                           datetime.datetime.fromtimestamp(to_timestamp / 1_000)
        except (OSError, OverflowError, ValueError):
            raise BadRequest('Bad timestamp data')

        query = db.session.query(Run) \
            .join(Problem) \
            .filter(Problem.problem_identity == problem_identity) \
            .filter(Run.context_identity == context_identity)

        if uids:
            query = query.filter(Run.user_identity.in_(uids))
        if lang_id:
            query = query.filter(Run.ejudge_language_id == lang_id)
        if status_id:
            query = query.filter(Run.ejudge_status == status_id)
        if from_timestamp:
            query = query.filter(Run.create_time > from_timestamp)
        if to_timestamp:
            query = query.filter(Run.create_time < to_timestamp)

        result = query.paginate(page=page, per_page=per_page_count, max_per_page=100)

        runs = []
        for run in result.items:
            # Это для сериалайзера
            run.problem_identity = problem_identity
            runs.append(run)

        metadata = {
            'count': result.total,
            'page_count': result.pages
        }

        schema = RunSchema(many=True)
        data = schema.dump(runs)

        return jsonify({'runs': data.data, 'metadata': metadata})

    def post(self, problem_identity: str, context_identity: str = None):
        args = parser.parse(post_args)

        language_id = args['lang_id']
        uid = args.get('uid')
        file = parser.parse_files(request, 'file', 'file')

        problem = db.session.query(Problem)\
            .filter(Problem.problem_identity == problem_identity).one_or_none()
        if not problem:
            raise NotFound('Problem with this uid is not found')

        try:
            text = self._check_file_restriction(file)
        except ValueError as e:
            raise BadRequest(e.args[0])
        source_hash = Run.generate_source_hash(text)

        duplicate = db.session.query(Run)\
            .filter(Run.user_identity == uid) \
            .filter(Run.problem_id == problem.id) \
            .filter(Run.context_identity == context_identity) \
            .order_by(Run.create_time.desc()).first()
        if duplicate is not None and duplicate.source_hash == source_hash:
            raise BadRequest('Source file is duplicate of previous submission')

        run = Run(
            user_identity=uid,
            problem=problem,
            problem_id=problem.id,
            context_identity=context_identity,
            ejudge_contest_id=problem.ejudge_contest_id,
            ejudge_language_id=language_id,
            ejudge_status=377,  # In queue
            source_hash=source_hash,
        )

        db.session.add(run)
        db.session.commit()
        db.session.refresh(run)

        run.update_source(text)

        current_app.logger.info(f'Add new submission #{run.id} to queue')

        ejudge_url = current_app.config['EJUDGE_NEW_CLIENT_URL']
        _ = queue_submit(run.id, uid, ejudge_url)

        run.problem_identity = problem_identity
        schema = RunSchema()
        data = schema.dump(run)

        return jsonify(data.data, 201)

    def put(self, run_id, **___):
        args = request.get_json(force=True)
        args = args.get('run')
        if args is None:
            raise BadRequest('Expected run object')
        run = db.session.query(Run).get(run_id)
        if not run:
            raise NotFound('Run with current id not found')

        schema = RunSchema(partial=True, context={'instance': run})

        run, errors = schema.load(args)
        if errors:
            raise BadRequest(errors)

        db.session.commit()

        schema = RunSchema()

        data = schema.dump(run)

        return jsonify(data.data)

    @staticmethod
    def _check_file_restriction(file, max_size_kb: int = 64) -> bytes:
        """ Function for checking submission restricts
            Checks only size (KB less then max_size_kb)
                and that is is not empty (len > 2)
            Raises
            --------
            ValueError if restriction is failed
        """
        max_size = max_size_kb * 1024
        file_bytes: bytes = file.read(max_size)
        if len(file_bytes) == max_size:
            raise ValueError('Submission should be less than 64Kb')
        # TODO: 4 это прото так, что такое путой файл для ejudge?
        if len(file_bytes) < 4:
            raise ValueError('Submission shouldn\'t be empty')

        return file_bytes
