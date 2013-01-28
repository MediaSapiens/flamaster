from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


product = Blueprint('product', __name__, url_prefix='/product')

db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)
mongo = LocalProxy(lambda: current_app.extensions['mongoset'])
mail = LocalProxy(lambda: current_app.extensions['mail'])


class OrderStates(object):
    created = 0
    paid = 1
    delivered = 2
    complete = 3
    customer_canceled = 5
    merchant_canceled = 7


# from .models import *
# from .documents import *
from .exceptions import ShelfNotAvailable

import api, signals, views
