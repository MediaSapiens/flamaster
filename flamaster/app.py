from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

import os


blueprints = {
    'core': 'flamaster.core.views',
    'account': 'flamaster.account.api'
}


def register_blueprints(app, **blueprints):
    for bp, module in blueprints.itervalues():
        bp_module = __import__(module, {}, {}, [''])
        app.register_blueprint(vars(bp_module)[bp])
    return app


def register_assets(app):
    assets = Environment(app)
    assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
    assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
    assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))
    return app

app = Flask(__name__, static_url_path='/static', template_folder='static')
if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.local_test_settings')
else:
    app.config.from_object('flamaster.conf.settings')
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'

app = register_blueprints(app, **blueprints)
app = register_assets(app)
db = SQLAlchemy(app)
