from flask import Blueprint

from core.controllers.problem import ProblemRunApi
from core.controllers.run_source import RunSourceApi

problem_blueprint = Blueprint('problem', __name__, url_prefix='/problem')

problem_blueprint.add_url_rule('/<problem_identity>/run',
                               view_func=ProblemRunApi.as_view('problem_runs'),
                               methods=('GET', 'POST', ))

problem_blueprint.add_url_rule('/<problem_identity>/context/<context_identity>/run',
                               view_func=ProblemRunApi.as_view('problem_context_runs'),
                               methods=('GET', 'POST', ))

problem_blueprint.add_url_rule('/<problem_identity>/run/<int:run_id>',
                               view_func=RunSourceApi.as_view('problem_runs_update'),
                               methods=('GET', ))
