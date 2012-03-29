from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

import os

blueprints = ['core', 'account',
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'
]


app = Flask(__name__, static_url_path='/static', template_folder='static')
if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.local_test_settings')
else:
    app.config.from_object('flamaster.conf.settings')

db = SQLAlchemy(app)

for blueprint in blueprints:
    bp_module = __import__('flamaster.%s' % blueprint, {}, {}, [''])
    app.register_blueprint(getattr(bp_module, blueprint))


assets = Environment(app)

assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))
