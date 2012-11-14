from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


bp = Blueprint('flatpages', __name__, url_prefix='/flatpages')

db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)

import models, api
# import utils
