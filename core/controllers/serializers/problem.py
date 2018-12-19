from marshmallow import Schema, post_load, fields

from core.models import Problem


class ProblemSchema(Schema):
    problem_identity = fields.String(dump_only=True)
    ejudge_contest_id = fields.Integer(required=True)
    ejudge_problem_id = fields.Integer(required=True)
    samples = fields.Method(serialize='serialize_samples')

    @post_load
    def load_problem(self, data):
        """Get an ORM object to be loaded."""
        problem = self.context.get('instance', Problem())

        for attr, value in iter(data.items()):
            setattr(problem, attr, value)

        return problem

    @staticmethod
    def serialize_samples(obj: Problem):
        pass
