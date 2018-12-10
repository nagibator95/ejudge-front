import datetime
import hashlib
from typing import Optional

from core.plugins import mongo
from core.models.base import db, UNIQUE_IDENTITY_SIZE


class Run(db.Model):

    __tablename__ = 'run'

    id = db.Column(db.Integer, primary_key=True)

    user_identity = db.Column(db.String(UNIQUE_IDENTITY_SIZE), nullable=False)
    context_identity = db.Column(db.String(UNIQUE_IDENTITY_SIZE))
    ejudge_identity = db.Column(db.String(UNIQUE_IDENTITY_SIZE))

    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship('Problem', backref=db.backref('runs'))

    create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Поля скопированные из ejudge.runs
    ejudge_run_id = db.Column('ej_run_id', db.Integer)
    ejudge_contest_id = db.Column('ej_contest_id', db.Integer)
    ejudge_run_uuid = db.Column('ej_run_uuid', db.String(40))

    ejudge_score = db.Column('ej_score', db.Integer)
    ejudge_status = db.Column('ej_status', db.Integer)
    ejudge_language_id = db.Column('ej_lang_id', db.Integer)
    ejudge_test_num = db.Column('ej_test_num', db.Integer)

    ejudge_create_time = db.Column('ej_create_time', db.DateTime)
    ejudge_last_change_time = db.Column('ej_last_change_time', db.DateTime)
    ejudge_url = db.Column(db.String(50))

    source_hash = db.Column(db.String(UNIQUE_IDENTITY_SIZE))  # We are using md5 hex digest

    def update_source(self, blob: bytes):
        mongo.db.source.insert_one({
            'run_id': self.id,
            'blob': blob,
        })
        return blob

    @property
    def source(self) -> Optional[bytes]:
        data = mongo.db.source.find_one({'run_id': self.id})
        if not data:
            # TODO: Совсем забыл про ejudge_run, который в ejudge.runs
            # TODO: Но тут проще при миграции просто засунуть всё в Mongo
            text = self.ejudge_run.get_sources()
            if not text:
                return None
            blob = text.decode('utf-8')
            self.update_source(blob)
            return blob
        blob = data.get('blob', None)
        return blob

    @staticmethod
    def generate_source_hash(blob: bytes) -> str:
        m = hashlib.md5()
        m.update(blob)
        return m.hexdigest()

    @property
    def status(self):
        return self.ejudge_status

    @property
    def language_id(self):
        return self.ejudge_language_id

    @staticmethod
    def pick_ejudge_columns(ejudge_run):
        return {
            'ejudge_run_id': ejudge_run.run_id,
            'ejudge_contest_id': ejudge_run.contest_id,
            'ejudge_run_uuid': ejudge_run.run_uuid,
            'ejudge_score': ejudge_run.score,
            'ejudge_status': ejudge_run.status,
            'ejudge_language_id': ejudge_run.lang_id,
            'ejudge_test_num': ejudge_run.test_num,
            'ejudge_create_time': ejudge_run.create_time,
            'ejudge_last_change_time': ejudge_run.last_change_time,
        }

    @staticmethod
    def from_ejudge_run(ejudge_run):
        run = Run(
            user=ejudge_run.user,
            problem=ejudge_run.problem,
            score=ejudge_run.score,
            **Run.pick_ejudge_columns(ejudge_run),
        )
        return run
