from flask import Blueprint


product = Blueprint('product', __name__, template_folder='templates',
                    url_prefix='product')

try:
    from views import *
except ImportError:
    pass