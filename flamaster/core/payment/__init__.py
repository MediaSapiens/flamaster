from flask import Blueprint


payment = Blueprint('payment', __name__, template_folder='templates',
                    url_prefix='payment')

try:
    from views import *
except ImportError:
    pass