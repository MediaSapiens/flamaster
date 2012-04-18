from flask import Blueprint

core = Blueprint('core', __name__, url_prefix='')

from views import *
from filters import *
