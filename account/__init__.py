from flask import Blueprint, current_app
from werkzeug.local import LocalProxy

bp = Blueprint('account', __name__, url_prefix='/account')

_security = LocalProxy(lambda: current_app.extensions['security'])
_social = LocalProxy(lambda: current_app.extensions['social'])
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)

import models, signals, api
