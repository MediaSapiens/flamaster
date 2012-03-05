from flask import Blueprint


delivery = Blueprint('delivery', __name__, template_folder='templates',
                    url_prefix='delivery')

try:
    from views import *
except ImportError:
    pass