# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import logging
import requests

from flask import redirect, url_for, request, json, Response
from urlparse import parse_qsl

from flamaster.core import db
from flamaster.product.models import PaymentTransaction, Order, Cart
from flamaster.product.datastore import PaymentTransactionDatastore
from flamaster.product.signals import order_created

from .base import BasePaymentMethod


CURRENCY = 'EUR'
ACTION = 'SALE'
SET_CHECKOUT = 'SetExpressCheckout'
GET_CHECKOUT = 'GetExpressCheckoutDetails'
DO_PAYMENT = 'DoExpressCheckoutPayment'
RESPONSE_OK = 'Success'
logger = logging.getLogger(__name__)


class PayPalPaymentMethod(BasePaymentMethod):
    """ PayPal API handler. Designed to use only express checkout methods.
        See https://www.x.com/developers/paypal/documentation-tools/express-checkout/how-to/ht_ec-singleItemPayment-curl-etc

        Collecting a one-time payment with PayPal requires:

            Setting up the payment information.:w
            Redirecting the customer to PayPal for authorization.
            Obtaining authorized payment details.
            Capturing the payment.
    """
    method_name = 'paypal'

    def __do_request(self, request_params):
        """ Directly request
        """
        request_params.update(self.settings)
        resp = requests.get(self.endpoint, params=request_params)
        return dict(parse_qsl(resp.text))

    def __set_checkout(self, amount):
        """ When a customer is ready to check out, use the SetExpressCheckout
            call to specify the amount of payment, return URL, and cancel
            URL. The SetExpressCheckout response contains a token for use in
            subsequent steps.
            Step 2 contained. Redirect the Customer to PayPal for
            Authorization.
        """
        request_params = {
            'METHOD': SET_CHECKOUT,
            'PAYMENTREQUEST_0_AMT': amount,
            'PAYMENTREQUEST_0_PAYMENTACTION': ACTION,
            'PAYMENTREQUEST_0_CURRENCYCODE': CURRENCY,
            # FIXME: BuildError
            'RETURNURL': request.url_root.rstrip('/') + url_for(
                                            'payment.process_payment',
                                            payment_method=self.method_name),
            'CANCELURL': request.url_root.rstrip('/') + url_for(
                                            'payment.cancel_payment',
                                            payment_method=self.method_name)
        }
        response = self.__do_request(request_params)

        if response['ACK'] == RESPONSE_OK:
            webface_url = self.__get_redirect_url(response)
            print webface_url
            PaymentTransaction.create(status=PaymentTransaction.ACCEPTED,
                                      details=response['TOKEN'],
                                      order_data=self.order_data)
            return redirect(webface_url)

        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name))

    def __capture_payment(self, response):
        """ Final step. The payment can be captured (collected) using the
            DoExpressCheckoutPayment call.
        """
        tnx = PaymentTransaction.query.filter_by(details=response['TOKEN']).first()

        if tnx is None:
            return redirect(url_for('payment.error_payment',
                                    payment_method=self.method_name))

        request_params = {
            'METHOD': DO_PAYMENT,
            'TOKEN': response['TOKEN'],
            'PAYERID': response['PAYERID'],
            'PAYMENTREQUEST_0_AMT': self.order_data['total_price'],
            'PAYMENTREQUEST_0_PAYMENTACTION': ACTION,
            'PAYMENTREQUEST_0_CURRENCYCODE': CURRENCY,
        }
        response = self.__do_request(request_params)

        if response['ACK'] == RESPONSE_OK:
            transaction_ds = PaymentTransactionDatastore(Order, Cart)
            order = Order.create(**tnx.order_data)
            goods = self.goods_ds.find(customer=tnx.order_data.get('customer'),
                                       is_ordered=False)
            transaction_ds.process(tnx, order, goods)
            db.session.commit()
            order_created.send(order)

            return Response(response=json.dumps(response), status=201,
                            mimetype='application/json')

        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name))

    def __get_payment_details(self, token, PayerID):
        """ If the customer authorizes the payment, the customer is redirected
            to the return URL that you specified in the SetExpressCheckout
            call. The return URL is appended with the same token as the token
            used above.
        """
        request_params = {
            'METHOD': GET_CHECKOUT,
            'TOKEN': token,
            'PAYERID': PayerID
        }

        response = self.__do_request(request_params)

        if response['ACK'] == RESPONSE_OK:
            return self.__capture_payment(response)

        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name))

    def init_payment(self):
        """ Initialization payment process.
        """
        return self.__set_checkout(self.order_data['total_price'])

    def process_payment(self):
        return self.__get_payment_details(**dict(request.args))

    def __get_redirect_url(self, response):
        face = "https://www.{}paypal.com/webscr?cmd=_express-checkout&token={}"
        return face.format(self.sandbox and 'sandbox.' or '',
                           response['TOKEN'])

    @property
    def endpoint(self):
        endpoint_args = (self.settings['SIGNATURE'] and '-3t' or '',
                         self.sandbox and 'sandbox.' or '',)
        return 'https://api{}.{}paypal.com/nvp'.format(*endpoint_args)
