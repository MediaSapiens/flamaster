from flask import Blueprint


statistic = Blueprint('statistic', __name__, template_folder='templates',
                    url_prefix='statistic')

try:
    from views import *
except ImportError:
    pass