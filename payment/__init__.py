from flask import Blueprint

payment = Blueprint('payment', __name__, url_prefix='/payment')

from methods.base import *
