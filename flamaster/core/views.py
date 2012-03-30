from flask  import render_template
from flask.helpers import json, _assert_have_json
from flask import current_app, request, Blueprint

from sqlalchemy.orm import class_mapper


def jsonify(*args, **kwargs):
    status = 200
    if __debug__:
        _assert_have_json()
    if 'status' in kwargs:
        status = kwargs.pop('status', 200)
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
        indent=None if request.is_xhr else 2), status=status,
        mimetype='application/json')


def as_dict(obj):
    return dict((c.name, getattr(obj, c.name))
              for c in class_mapper(obj.__class__).mapped_table.c)

core = Blueprint('core', __name__, url_prefix='')

#__all__ = ['index', 'core']

@core.route('/')
def index():
    return render_template('index.html', **{})
