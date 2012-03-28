from flask  import render_template
from . import core


@core.route('/')
def app_index():
    return render_template('index.html', **{})
