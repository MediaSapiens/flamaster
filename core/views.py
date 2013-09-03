from __future__ import absolute_import
from jinja2.exceptions import TemplateNotFound
from flask import abort, render_template, current_app

from . import core


__all__ = ['index', 'template']


# @core.route('/')
def index():
    return render_template('base.html', **{})


@core.route('/templates/<path:template>')
@core.route('/templates/')
def template(template=None):
    template or abort(404)

    try:
        return render_template(current_app.jinja_env.get_template(template))
    except TemplateNotFound:
        abort(404)
