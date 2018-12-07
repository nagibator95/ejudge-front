from flask import jsonify as flask_jsonify


def jsonify(data, status_code=200):
    response = {
        'status_code': status_code,
    }
    if status_code in (200, 201):
        response['data'] = data
        response['status'] = 'success'
    else:
        response['error'] = data
        response['status'] = 'error'

    return flask_jsonify(response), status_code


def attrs_to_dict(obj, *attrs):
    return {
        attr: getattr(obj, attr, None)
        for attr in attrs
    }