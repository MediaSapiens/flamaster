from flask import Blueprint


product = Blueprint('product', __name__, url_prefix='/product')

from .api import *
from .models import *
