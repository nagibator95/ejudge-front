from marshmallow import Schema, fields


class RunSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_identity = fields.String()
    context_identity = fields.String()
    ejudge_identity = fields.String()
    ejudge_status = fields.String()

    problem_identity = fields.String(dump_only=True)

    create_time = fields.DateTime(dump_only=True)
