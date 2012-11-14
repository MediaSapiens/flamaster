# PayPal configurations
SANDBOX_ENV = True # if `False` it is all be truly
SIGNATURE_AUTH = True # if `True` auth would be done with signature else with certificate


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, settings, order):
        self.settings = settings

    def process_payment(self, amount, currency, description):
        raise NotImplemented()

    def method(self, case):
        """ The API operation you are addressing
        """
        raise NotImplementedError

    def amount(self, total):
        """ Calculate payment cash amount
        """
        raise NotImplementedError

    def headers(self):
        """ Provide request headers
        """
        raise NotImplementedError

    @property
    def endpoint(self):
        endpoint_args = (SIGNATURE_AUTH and '-3t' or '',
                SANDBOX_ENV and 'sandbox' or '')
        return 'https://api{}.{}paypal.com/nvp'.format(endpoint_args)
