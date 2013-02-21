from flask import Blueprint


product = Blueprint('product', __name__, url_prefix='/product')


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

import api, signals
