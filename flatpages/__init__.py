from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


flatpages = Blueprint('flatpages', __name__, url_prefix='/flatpages')
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)


import api
import models
# import utils
