from flask import Blueprint
from flamaster.core.utils import add_api_rule

bp = Blueprint('delivery', __name__, url_prefix='/delivery')

def add_resource(endpoint, pk_def, import_name):
    return add_api_rule(bp, endpoint, pk_def,
                        'flamaster.delivery.api.{}'.format(import_name))

add_resource('options', {'id': int}, 'ProductDeliveryResource')


import models