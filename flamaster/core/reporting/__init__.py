from flask import Blueprint


reporting = Blueprint('reporting', __name__, template_folder='templates',
                    url_prefix='reporting')

try:
    from views import *
except ImportError:
    pass