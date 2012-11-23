from flask import current_app, render_template

from .. import payment
from flamaster.core.utils import resolve_payment_method
from flamaster.product.models import Order


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, order=Order):
        my_method = current_app.config['PAYMENT_METHODS'][self.method_name]
        self.settings = my_method['settings']
        self.sandbox = my_method['SANDBOX']
        self.order = order

    def init_payment(self, amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError


@payment.route('/<payment_method>/process')
def process_payment(payment_method):
    PaymentMethod = resolve_payment_method(payment_method)
    order_data = PaymentMethod().process_payment()
    return render_template('success_order.html', order=order_data)


@payment.route('/<payment_method>/cancel')
def cancel_payment(payment_method):
    return render_template('cancel.html')


@payment.route('/<payment_method>/error')
def error_payment(payment_method):
    return render_template('error.html')
