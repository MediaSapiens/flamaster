from flask import Blueprint, render_template


core = Blueprint('core', __name__, url_prefix='')


@core.route('/')
def index():
    return render_template('index.html', **{})
