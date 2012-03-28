from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

import os

blueprints = [
    'account', 'core'
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'
]

db = SQLAlchemy()


def create_app(db):
    app = Flask(__name__, static_url_path='/static', template_folder='static')
    if 'TESTING' in os.environ:
        app.config.from_object('flamaster.conf.local_test_settings')
    else:
        app.config.from_object('flamaster.conf.settings')

    db.init_app(app)
    return app


def register_blueprints(app, *args):
    for name in args:
        bp_module = __import__('flamaster.%s' % name, {}, {}, [''])
        app.register_blueprint(vars(bp_module)[name])
    print app.url_map
    return app


def register_assets(app):
    assets = Environment(app)

    assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
    assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
    assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))
    return app


def init_all(db):
    return register_assets(
                register_blueprints(
                    create_app(db),
                    *blueprints))

# register_blueprints(app, *blueprints)

