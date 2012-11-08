class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    _endpoint = ''
    _cancel_url = ''
    _return_url = ''
    _format = ''

    def call(self):
        """ Provide all call elements and meke request
        """
        raise NotImplementedError

    def paylod(self):
        """ Provide call payloads
        """
        raise NotImplementedError

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
