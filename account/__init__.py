from flask import Blueprint, current_app
from werkzeug.local import LocalProxy

app = LocalProxy(lambda: current_app)
_security = LocalProxy(lambda: app.extensions['security'])
_social = LocalProxy(lambda: app.extensions['social'])
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)

account = Blueprint('account', __name__, url_prefix='/account')

import signals
import permissions

import api
