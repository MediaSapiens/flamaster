from flask import Blueprint, current_app
from werkzeug.local import LocalProxy

payment = Blueprint('payment', __name__, url_prefix='/payment')
mongo = LocalProxy(lambda: current_app.extensions['mongoset'])

from methods.base import *
