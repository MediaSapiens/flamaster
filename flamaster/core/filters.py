from flask.helpers import json
from flamaster.app import app

from .utils import CustomEncoder


@app.template_filter('rstrip')
def rstrip(value, string):
    """ filter that brings standart string.rstrip method functionality into
        template context
    """
    return value.rstrip(string)


@app.template_filter('to_custom_json')
def to_custom_json(value):
    return json.dumps(value, indent=2, cls=CustomEncoder)
