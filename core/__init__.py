from logging.config import dictConfig

from flask import Flask

from core.models.base import db
from core.plugins import mongo, redis
from core.utils import register_error_handlers


def create_app():

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['stdout']
        }
    })

    app = Flask(__name__)

    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_envvar('CORE_SETTINGS', silent=True)

    db.init_app(app)
    mongo.init_app(app)
    redis.init_app(app)

    register_error_handlers(app)

    return app

