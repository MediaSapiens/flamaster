from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.assets import Environment, Bundle
from flask.ext.mail import Mail

import os


app = Flask(__name__, static_url_path='/static', template_folder='static')
mail = Mail(app)
db = SQLAlchemy(app)


from core import core
from account import account

app.register_blueprint(core)
app.register_blueprint(account)

# blueprints = ['core', 'account']


# def register_blueprints(app, blueprints):
#     for bp in blueprints:
#         bp_module = __import__("flamaster.{}".format(bp), {}, {}, [''])
#         app.register_blueprint(vars(bp_module)[bp])
#     return app


def register_assets(app):
    assets = Environment(app)
    assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
    assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
    assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))
    return app


# def register_signals(app, blueprints):
#     for bp in blueprints:
#         try:
#             __import__("flamaster.{}.signals".format(bp), {}, {}, [''])
#         except ImportError as e:
#             print bp, e.message
#     return app

if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.local_test_settings')
else:
    app.config.from_object('flamaster.conf.settings')
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'

# app = register_blueprints(app, blueprints)
app = register_assets(app)
