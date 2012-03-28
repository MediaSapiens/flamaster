from flask import render_template
from . import account


__all__ = ['index']


@account.route('/')
def index():
    return render_template('account/index.html')
