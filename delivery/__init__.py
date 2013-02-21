from flask import Blueprint

bp = Blueprint('delivery', __name__, url_prefix='/delivery')

import models
import api
