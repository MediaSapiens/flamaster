from flask import render_template

from . import core


__all__ = ['index']


@core.route('/')
def index():
    return render_template('base.html', **{})
