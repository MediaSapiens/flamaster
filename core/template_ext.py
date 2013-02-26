from __future__ import absolute_import
from flask import current_app, json

from .utils import CustomEncoder


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
