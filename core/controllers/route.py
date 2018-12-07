from flask import Blueprint

from core.controllers.problem import ProblemRuns

problem_blueprint = Blueprint('problem', __name__, url_prefix='/problem')

problem_blueprint.add_url_rule('/<str:problem_identity>/run',
                               view_func=ProblemRuns.as_view('problem_runs'),
                               methods=('GET', 'POST', ))

problem_blueprint.add_url_rule('/<str:problem_identity>/context/<str:context_identity>/run',
                               view_func=ProblemRuns.as_view('problem_runs'),
                               methods=('GET', 'POST', ))
