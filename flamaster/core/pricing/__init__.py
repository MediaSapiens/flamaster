from flask import Blueprint


pricing = Blueprint('pricing', __name__, template_folder='templates',
                    url_prefix='pricing')

try:
    from views import *
except ImportError:
    pass