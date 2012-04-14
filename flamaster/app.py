from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy, models_committed
from flask.ext.assets import Environment, Bundle

import os


app = Flask(__name__, static_url_path='/static', template_folder='static')
db = SQLAlchemy(app)

blueprints = {
    'core': 'flamaster.core.views',
    'account': 'flamaster.account.api'}


def register_blueprints(app, blueprints):
    for bp, module in blueprints.iteritems():
        bp_module = __import__(module, {}, {}, [''])
        app.register_blueprint(vars(bp_module)[bp])
    return app


def register_assets(app):
    assets = Environment(app)
    assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
    assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
    assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))
    return app


def register_signals(app, blueprints):
    for bp in blueprints.iterkeys():
        try:
            signal_module = __import__("flamaster.{}.signals".format(bp), {},
                                       {}, [''])
            module_vars = vars(signal_module)
            signals = filter(lambda s: s.endswith('_signal'),
                             module_vars.keys())
            for signal in signals:
                models_committed.connected_to(module_vars[signal], sender=app)
        except ImportError as e:
            pass
    return app

if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.local_test_settings')
else:
    app.config.from_object('flamaster.conf.settings')
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'

app = register_blueprints(app, blueprints)
app = register_signals(app, blueprints)
app = register_assets(app)
