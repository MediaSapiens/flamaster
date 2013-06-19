from flask import Blueprint
from flamaster.core.utils import add_api_rule

from .exceptions import ShelfNotAvailable
from .signals import *


class OrderStates(object):
    created = 0
    paid = 1
    delivered = 2
    complete = 3
    customer_canceled = 5
    merchant_canceled = 7

product = Blueprint('product', __name__, url_prefix='/product')


def add_resource(endpoint, pk_def, import_name):
    return add_api_rule(product, endpoint, pk_def,
                        'flamaster.product.api.{}'.format(import_name))


add_resource('categories', {'id': int}, 'CategoryResource')
add_resource('countries', {'id': int}, 'CountryResource')




