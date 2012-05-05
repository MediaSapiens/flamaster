from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.assets import Environment, Bundle
from flask.ext.mail import Mail

import os


app = Flask(__name__, static_url_path='/static', template_folder='static')


# if 'runtests' in os.environ['_']:
#     app.config.from_object('flamaster.conf.local_test_settings')
# else:
#     app.config.from_object('flamaster.conf.settings')
# app.config.from_object('flamaster.conf.local_test_settings')
app.config.from_object('flamaster.conf.settings')


mail = Mail(app)
db = SQLAlchemy(app)
assets = Environment(app)

less = Bundle(
  'css/bootstrap.css',
  Bundle('less/style.less', filters='less', output='gen/less.css', debug=False),
  filters='yui_css', output='gen/style.css'
)

assets.register('style_base', less)

from core import core
from account import account
from product import product

app.register_blueprint(core)
app.register_blueprint(account)
app.register_blueprint(product)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
# blueprints = ['core', 'account']


# def register_blueprints(app, blueprints):
#     for bp in blueprints:
#         bp_module = __import__("flamaster.{}".format(bp), {}, {}, [''])
#         app.register_blueprint(vars(bp_module)[bp])
#     return app
