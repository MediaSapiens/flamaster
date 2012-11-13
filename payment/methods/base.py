class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, settings, order):
        self.settings = settings

    def process_payment(self, amount, currency, description):
        raise NotImplemented()

