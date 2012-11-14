from flask import current_app
from flamaster.product.models import Order

# PayPal configurations
SANDBOX_ENV = True # if `False` it is all be truly
SIGNATURE_AUTH = True # if `True` auth would be done with signature else with certificate


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, order=Order):
        self.settings = current_app.config[
                '{}_SETTINGS'.format(self.method_name.upper())
                ]
        self.order = order

    def init_payment(self, amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError

    def headers(self):
        """ Provide request headers
        """
        raise NotImplementedError

