from flask import Blueprint


category = Blueprint('category', __name__, template_folder='templates',
                     url_prefix='category')

try:
    from views import *
except ImportError:
    pass