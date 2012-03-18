from flask.helpers import json, _assert_have_json
from flask import current_app, request


def jsonify(*args, **kwargs):
    status = 200
    if __debug__:
        _assert_have_json()
    if 'status' in kwargs:
        status = kwargs.pop('status', 200)
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
        indent=None if request.is_xhr else 2), status=status,
        mimetype='application/json')
