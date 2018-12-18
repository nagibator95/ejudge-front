from marshmallow import Schema, fields, post_load

from core.models import Run


class RunSchema(Schema):
    id = fields.Integer(dump_only=True)

    user_identity = fields.String(dump_only=True)
    context_identity = fields.String(dump_only=True)
    problem_identity = fields.String(dump_only=True)

    ejudge_identity = fields.String(dump_only=True)
    ejudge_status = fields.Integer()

    language_id = fields.String(dump_only=True)
    create_time = fields.DateTime(dump_only=True)
    ejudge_last_change_time = fields.DateTime(dump_only=True)

    @post_load
    def load_course(self, data):
        """Get an ORM object to be loaded."""
        run = self.context.get('instance', Run())

        for attr, value in iter(data.items()):
            setattr(run, attr, value)

        return run
