from flask import request
from werkzeug.exceptions import Forbidden


def get_api_key_checker(key) -> callable:
    """ Function which returns function which checks request api key
    Basic usage:
        app = Flask()
        app.before_request(get_api_key_checker(<my-secret-string>))
    Raises
        ------
        Forbidden: when api key is bad or not allowed
    """
    def check_api_key():
        requested_key = request.headers.get('api-key')
        if key != requested_key:
            raise Forbidden('API key is not valid!')

    return check_api_key
