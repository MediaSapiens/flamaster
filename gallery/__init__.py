from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


bp = Blueprint('gallery', __name__, url_prefix='/gallery')

db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)

import models, api
