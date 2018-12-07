import flask_testing
import unittest
import sys

from core import create_app
from core.models import db
from core.plugins import mongo, redis


class TestCase(flask_testing.TestCase):
    CONFIG = {
        'SERVER_NAME': 'localhost',
        'URL_ENCODER_ALPHABET': 'abc',
    }

    def create_app(self):
        app = create_app()
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        assert mongo.db.name == 'test'
        mongo.db.client.drop_database(mongo.db)

        redis.flushdb()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        path = 'tests'
    else:
        path = sys.argv[1]

    try:
        tests = unittest.TestLoader().discover(path)
    except:
        tests = unittest.TestLoader().loadTestsFromName(path)

    result = unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()
    sys.exit(not result)

