from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

import os

app = Flask(__name__, static_url_path='/static', template_folder='static')
if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.local_test_settings')
else:
    app.config.from_object('flamaster.conf.settings')

db = SQLAlchemy(app)

from flamaster.account.views import account as accountModule
from flamaster.core.views import core as coreModule

app.register_blueprint(accountModule)
app.register_blueprint(coreModule)

assets = Environment(app)

assets.register('js_vendor', Bundle('js/vendor.js', output='gen/v.js'))
assets.register('js_templates', Bundle('js/templates.js', output='gen/t.js'))
assets.register('js_app', Bundle('js/app.js', output='gen/a.js'))
