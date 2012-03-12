from flask import render_template
from . import account


@account.route('/')
def index():
    return render_template('account/index.html')
