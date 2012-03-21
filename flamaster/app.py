from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__, static_url_path='/static', template_folder='static')
app.config.from_object('flamaster.conf.settings')
db = SQLAlchemy(app)

blueprints = [
    'account',
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'
]


def register_blueprints(app, *args):
    for name in args:
        bp_module = __import__('flamaster.%s' % name, {}, {}, [''])
        app.register_blueprint(vars(bp_module)[name], url_prefix="/%s" % name)

register_blueprints(app, *blueprints)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def access_denied(e):
    return render_template('403.html'), 403


@app.route('/')
def app_index():
    return render_template('index.html', **{})
