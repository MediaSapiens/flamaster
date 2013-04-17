from flask import Blueprint
from flask.ext.babel import lazy_gettext as _


product = Blueprint('product', __name__, url_prefix='/product')


class OrderStates(object):
    created = 0
    paid = 1
    delivered = 2
    complete = 3
    customer_canceled = 5
    merchant_canceled = 7


order_states_i18n = {
    '0': _('Created'),
    '1': _('Paid'),
    '2': _('Delivered'),
    '3': _('Complete'),
    '5': _('Customer Canceled'),
    '7': _('Merchant Canceled')
}

# from .models import *
# from .documents import *
from .exceptions import ShelfNotAvailable

import api, signals
