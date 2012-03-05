from flask import Blueprint


tax = Blueprint('tax', __name__, template_folder='templates',
                    url_prefix='tax')

try:
    from views import *
except ImportError:
    pass