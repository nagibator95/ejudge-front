from flask_migrate import Migrate
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis

redis_client = FlaskRedis()

migrate = Migrate()

mongo = PyMongo()
