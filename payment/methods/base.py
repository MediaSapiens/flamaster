from flask.views import View
from flask import current_app, render_template

from flamaster.product.models import Order

# PayPal configurations
SANDBOX_ENV = True # if `False` it is all be truly
SIGNATURE_AUTH = True # if `True` auth would be done with signature else with certificate


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, order):
        self.settings = current_app.config['PAYMENT_METHODS'][self.method_name]
        self.order = order

    def init_payment(self, amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError

    def headers(self):
        """ Provide request headers
        """
        raise NotImplementedError


# If no more methods required should be a single function
class InitPaymentView(View):
    """ The view redirects user to authorize payment
    """
    PAYMENT_METHOD = BasePaymentMethod

    def dispatch_request(self, amount, currency, customer_id):
        order = Order.create(customer_id=customer_id)

        return BasePaymentMethod(order).init_payment(amount, currency)


class ProcessPaymentView(View):
    """ Capture payment and show to user an order data
    """
    def dispatch_request(self, token):
        order_data = BasePaymentMethod().process_payment(token)
        return render_template('success_order.html', order=order_data)
