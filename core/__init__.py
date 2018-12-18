from logging.config import dictConfig

from flask import Flask

from core.controllers.route import problem_blueprint
from core.models.base import db
from core.plugins import mongo, redis_client, migrate
from core.utils.exceptions import register_error_handlers
from core.utils.auth import get_api_key_checker


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
    migrate.init_app(app, db)

    mongo.init_app(app)
    redis_client.init_app(app)

    app.register_blueprint(problem_blueprint)

    register_error_handlers(app)

    if not app.config.get('DEBUG'):
        secret_key = app.config['SECRET_KEY']
        app.before_request(get_api_key_checker(secret_key))

    return app
