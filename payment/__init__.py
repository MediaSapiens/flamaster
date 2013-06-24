from flask import Blueprint, current_app

payment = Blueprint('payment', __name__, url_prefix='/payment')

import api
from methods.base import *
