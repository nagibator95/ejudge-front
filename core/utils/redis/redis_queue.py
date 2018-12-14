import pickle

from core.plugins import redis_client


class RedisQueue:
    def __init__(self, key):
        self.key = key

    def put(self, value, pipe=None):
        if pipe is None:
            pipe = redis_client

        pipe.rpush(self.key, pickle.dumps(value))

    def get(self, pipe=None):
        if pipe is None:
            pipe = redis_client

        value = pipe.lpop(self.key)
        if value:
            value = pickle.loads(value)
        return value

    def get_blocking(self, timeout=0, pipe=None):
        if pipe is None:
            pipe = redis_client

        value = pipe.blpop(self.key, timeout=timeout)
        if value:
            value = pickle.loads(value[1])
        return value
