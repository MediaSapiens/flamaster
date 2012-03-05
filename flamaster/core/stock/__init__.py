from flask import Blueprint


stock = Blueprint('stock', __name__, template_folder='templates',
                    url_prefix='stock')

try:
    from views import *
except ImportError:
    pass