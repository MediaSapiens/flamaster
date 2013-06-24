from __future__ import absolute_import
from flask import current_app, render_template, request, json
from werkzeug.utils import import_string

from .. import payment


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, goods=None, order_data=None):
        self.conf = current_app.config['PAYMENT_METHODS'][self.method_name]
        self.settings = self.conf.get('settings')
        self.sandbox = self.conf['SANDBOX']
        self.goods = goods
        self.order_data = order_data

    def verify(self, data):
        raise NotImplementedError

    def process_payment(self):
        raise NotImplementedError

    def init_payment(self):  # amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError

    def check_status(self, transaction):
        raise NotImplementedError


def resolve_payment_method(payment_method):
    method = current_app.config['PAYMENT_METHODS'][payment_method]
    class_string = method['module']
    return import_string(class_string)


@payment.route('/<payment_method>/verify/', methods=['POST'])
def verify_payment(payment_method):
    PaymentMethod = resolve_payment_method(payment_method)
    data = request.json or request.form or json.loads(request.data)
    return PaymentMethod().verify(data)


@payment.route('/<payment_method>/process/', methods=['GET', 'POST'])
def process_payment(payment_method):
    PaymentMethod = resolve_payment_method(payment_method)
    return PaymentMethod().process_payment()


@payment.route('/<payment_method>/cancel/')
def cancel_payment(payment_method):
    return render_template('payment/cancel.html')


@payment.route('/<payment_method>/error/')
def error_payment(payment_method):
    return render_template('payment/error.html')


@payment.route('/<payment_method>/success/')
def success_payment(payment_method):
    return render_template('payment/success.html')
