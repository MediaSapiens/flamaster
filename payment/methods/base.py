from __future__ import absolute_import
from flask import current_app, render_template, request, json, session
from werkzeug.utils import import_string, redirect

from .. import payment


class BasePaymentMethod(object):
    """ Base API handler class, established with respect to the PayPal API.
    """
    method_name = 'base'

    def __init__(self, order=None):
        my_method = current_app.config['PAYMENT_METHODS'][self.method_name]
        self.settings = my_method.get('settings')
        self.sandbox = my_method['SANDBOX']
        self.order = order

    def verify(self, data):
        raise NotImplementedError

    def process_payment(self):
        raise NotImplementedError

    def init_payment(self, payment_details=None):  # amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
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
    origin = session.get('origin')
    if origin is None:
        return render_template('payment/cancel.html')
    else:
        return redirect(origin)


@payment.route('/<payment_method>/success/')
def success_payment(payment_method):
    return render_template('payment/success.html')


@payment.route('/<payment_method>/error/')
def error_payment(payment_method):
    return render_template('payment/error.html')
