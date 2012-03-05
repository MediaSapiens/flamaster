from flask import Blueprint


account = Blueprint('account', __name__, template_folder='templates',
                    url_prefix='account')

try:
    from views import *
except ImportError:
    pass