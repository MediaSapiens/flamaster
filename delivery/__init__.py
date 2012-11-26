from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


bp = Blueprint('delivery', __name__, url_prefix='/delivery')

db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)


import models
import api
