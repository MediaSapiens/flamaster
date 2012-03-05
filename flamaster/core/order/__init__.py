from flask import Blueprint


order = Blueprint('order', __name__, template_folder='templates',
                    url_prefix='order')

try:
    from views import *
except ImportError:
    pass