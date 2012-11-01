from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


thumbnail = Blueprint('thumbnail', __name__, url_prefix='/thumbnail',
                  template_folder='templates')
cache = LocalProxy(lambda: current_app.extensions['cache'].cache)


import views
