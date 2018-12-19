import uuid

from flask import request
from flask.views import MethodView
from marshmallow import fields
from webargs.flaskparser import parser
from werkzeug.exceptions import BadRequest, NotFound

from core.models import db
from core.controllers.serializers.problem import ProblemSchema
from core.models import Problem
from core.utils import jsonify

POSSIBLE_RETRIEVE_FIELDS = ['samples']


get_args = {
    'with_fields': fields.List(
        fields.String(validate=lambda s: s in POSSIBLE_RETRIEVE_FIELDS),
        missing=[]),
}


class ProblemApi(MethodView):
    def get(self, problem_identity):
        args = parser.parse(get_args, request)
        with_fields = args['with_fields']
        with_samples = 'samples' in with_fields

        # Do something with me!

        return jsonify(data.data, 200)

    def post(self):
        data = request.get_json(force=True).get('problem')
        if not data:
            raise BadRequest('Field `problem` required')

        # Do something with me!

        return jsonify(data, 201)

    def put(self, problem_identity):
        request_data = request.get_json(force=True)
        data = request_data.get('problem')
        if not data:
            raise BadRequest('Field `problem` required')

        # Do something with me!

        return jsonify(data, 200)
