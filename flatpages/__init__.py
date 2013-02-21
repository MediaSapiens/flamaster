from flask import Blueprint


bp = Blueprint('flatpages', __name__, url_prefix='/flatpages')

import models, api
# import utils
