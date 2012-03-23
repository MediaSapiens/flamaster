from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle


import os

blueprints = [
    'account',
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'
]

app = Flask(__name__, static_url_path='/static', template_folder='static')
assets = Environment(app)

assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))

if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.test_settings')
else:
    app.config.from_object('flamaster.conf.settings')

db = SQLAlchemy(app)


def register_blueprints(app, *args):
    for name in args:
        bp_module = __import__('flamaster.%s' % name, {}, {}, [''])
        app.register_blueprint(vars(bp_module)[name], url_prefix="/%s" % name)

register_blueprints(app, *blueprints)


@app.route('/')
def app_index():
    return render_template('index.html', **{})


