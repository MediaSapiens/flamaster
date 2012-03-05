from flask import Blueprint


image = Blueprint('image', __name__, template_folder='templates',
                    url_prefix='image')

try:
    from views import *
except ImportError:
    pass