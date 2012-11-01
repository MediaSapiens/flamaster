from flask.helpers import json

from . import app
from .utils import CustomEncoder, check_permission


""" Here comes someutility template filters
"""


@app.template_filter()
def rstrip(value, string):
    """ filter that brings standart string.rstrip method functionality into
        template context
    """
    return value.rstrip(string)


@app.template_filter()
def to_custom_json(value):
    return json.dumps(value, indent=2, cls=CustomEncoder)


app.jinja_env.globals['check_permission'] = check_permission
