from flask import current_app


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, order):
        my_method = current_app.config['PAYMENT_METHODS'][self.method_name]
        self.settings = my_method['settings']
        self.sandbox = my_method['SANDBOX']
        self.order = order

    def init_payment(self, amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError
