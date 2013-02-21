from __future__ import absolute_import
from flask import current_app
from flask.helpers import json

from .utils import CustomEncoder, check_permission


""" Here comes someutility template filters
"""


@current_app.template_filter()
def rstrip(value, string):
    """ filter that brings standart string.rstrip method functionality into
        template context
    """
    return value.rstrip(string)


@current_app.template_filter()
def to_custom_json(value):
    return json.dumps(value, indent=2, cls=CustomEncoder)


current_app.jinja_env.globals['check_permission'] = check_permission
