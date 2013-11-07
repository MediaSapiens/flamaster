from flask import Blueprint
from flamaster.core.utils import add_api_rule

from .exceptions import ShelfNotAvailable
from .signals import *

from flask.ext.babel import lazy_gettext as _


class OrderStates(object):
    created = 0
    paid = 1
    delivered = 2
    complete = 3
    processing = 4
    customer_canceled = 5
    refund = 6
    merchant_canceled = 7

    _TRANSLATIONS = {
        created: _('created'),
        paid: _('paid'),
        delivered: _('delivered'),
        complete: _('complete'),
        customer_canceled: _('canceled by customer'),
        merchant_canceled: _('canceled by merchant'),
        processing: _('processing'),
        refund: _('refund')
    }

    @classmethod
    def translate(cls, state):
        return cls._TRANSLATIONS[state]


product = Blueprint('product', __name__, url_prefix='/product')


def add_resource(endpoint, pk_def, import_name):
    return add_api_rule(product, endpoint, pk_def,
                        'flamaster.product.api.{}'.format(import_name))


add_resource('categories', {'id': int}, 'CategoryResource')
add_resource('countries', {'id': int}, 'CountryResource')




