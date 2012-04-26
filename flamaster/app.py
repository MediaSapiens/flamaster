from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.assets import Environment
from flask.ext.mail import Mail

import os


app = Flask(__name__, static_url_path='/static', template_folder='static')


if 'TESTING' in os.environ:
    app.config.from_object('flamaster.conf.local_test_settings')
else:
    app.config.from_object('flamaster.conf.settings')


mail = Mail(app)
db = SQLAlchemy(app)
assets = Environment(app)

assets.register('style_base', 'less/style.less', filters='less',
                output='gen/style.css')


from core import core
from account import account

app.register_blueprint(core)
app.register_blueprint(account)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
# blueprints = ['core', 'account']


# def register_blueprints(app, blueprints):
#     for bp in blueprints:
#         bp_module = __import__("flamaster.{}".format(bp), {}, {}, [''])
#         app.register_blueprint(vars(bp_module)[bp])
#     return app




#     js_libs = ['jquery-1.7.1', 'underscore-1.3.1', 'backbone-0.9.1',
#              'handlebars-1.0.0.beta.6', 'require-1.0.7']
#     files = map(lambda x: "js/vendor/{}.js".format(x), js_libs)
#     assets.register('js_vendor', Bundle(*files, filters='closure_js',
#                                      output='gen/vendor.js'))

#     return app


# def register_signals(app, blueprints):
#     for bp in blueprints:
#         try:
#             __import__("flamaster.{}.signals".format(bp), {}, {}, [''])
#         except ImportError as e:
#             print bp, e.message
#     return app
    # 'category', 'delivery', 'image', 'order', 'payment',
    # 'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'

# app = register_blueprints(app, blueprints)
