# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from collections import Mapping
from decimal import Decimal
from urlparse import parse_qsl

import requests
from flask import redirect, url_for, request, session, current_app

from flamaster.core.utils import jsonify_status_code
from flamaster.extensions import sentry
from flamaster.product import OrderStates
from flamaster.product.documents import BaseProduct
from flamaster.product.utils import get_order_class

from . import PAYPAL
from .base import BasePaymentMethod


CURRENCY = 'EUR'
ACTION = 'SALE'
SET_CHECKOUT = 'SetExpressCheckout'
GET_CHECKOUT = 'GetExpressCheckoutDetails'
DO_PAYMENT = 'DoExpressCheckoutPayment'
RESPONSE_OK = 'Success'


class PayPalPaymentMethod(BasePaymentMethod):
    """ PayPal API handler. Designed to use only express checkout methods.
        See https://www.x.com/developers/paypal/documentation-tools/express-checkout/how-to/ht_ec-singleItemPayment-curl-etc

        Collecting a one-time payment with PayPal requires:

            Setting up the payment information.:w
            Redirecting the customer to PayPal for authorization.
            Obtaining authorized payment details.
            Capturing the payment.
    """
    method_name = PAYPAL

    def __do_request(self, request_params):
        """ Directly request
        """
        request_params.update(self.settings)
        sentry.captureMessage('paypal request', extra=request_params)
        resp = requests.get(self.endpoint, params=request_params)
        response_parsed = dict(parse_qsl(resp.text))
        sentry.captureMessage('paypal response', extra=response_parsed)
        return response_parsed

    def __set_checkout(self, amount, payment_details):
        """ When a customer is ready to check out, use the SetExpressCheckout
            call to specify the amount of payment, return URL, and cancel
            URL. The SetExpressCheckout response contains a token for use in
            subsequent steps.
            Step 2 contained. Redirect the Customer to PayPal for
            Authorization.
        """
        session.update(payment_details)
        sentry.captureMessage('paypal details', extra=payment_details)

        request_params = {
            'METHOD': SET_CHECKOUT,
            'PAYMENTREQUEST_0_AMT': amount,
            'PAYMENTREQUEST_0_PAYMENTACTION': ACTION,
            'PAYMENTREQUEST_0_CURRENCYCODE': CURRENCY,
            'NOSHIPPING': 1,
            'REQCONFIRMSHIPPING': 0,
            # FIXME: BuildError
            'RETURNURL': self.url_root + url_for('payment.process_payment',
                                 payment_method=self.method_name),
            'CANCELURL': self.url_root + url_for('payment.cancel_payment',
                                 payment_method=self.method_name)
        }
        # include description for items added to cart
        request_params.update(self.__prepare_cart_items())
        sentry.captureMessage('paypal set checkout details',
                              extra=request_params)

        response = self.__do_request(request_params)
        if response['ACK'] == RESPONSE_OK:
            self.order.set_payment_details(token=response['TOKEN'])
            webface_url = self.__get_redirect_url(response)
            response = self.order.as_dict()
            response.update({
                'action': 'redirect',
                'target': webface_url
            })
            return jsonify_status_code(response)

        return {
            'action': 'redirect',
            'target': self.url_root + url_for('payment.error_payment',
                              payment_method=self.method_name)
        }

    def __prepare_cart_items(self):
        cart_items_request_params = {}
        tax = current_app.config['SHOPS'][current_app.config['SHOP_ID']]['tax']
        for idx, item in enumerate(self.order.goods):
            product = BaseProduct.objects(pk=item.product_id).first()
            item_category = current_app.config['DELIVERY_TO_PAYPAL'][item.details.delivery]
            cart_items_request_params.update({
                'L_PAYMENTREQUEST_0_ITEMCATEGORY{}'.format(idx): item_category,
                'L_PAYMENTREQUEST_0_TAXAMT{}'.format(idx): Decimal(tax),
                'L_PAYMENTREQUEST_0_QTY{}'.format(idx): item.amount,
                'L_PAYMENTREQUEST_0_AMT{}'.format(idx): item.price,
                'L_PAYMENTREQUEST_0_NAME{}'.format(idx): item.details_verbose,
                'L_PAYMENTREQUEST_0_DESC{}'.format(idx): product.name,
            })
        return cart_items_request_params

    def __capture_payment(self, response):
        """ Final step. The payment can be captured (collected) using the
            DoExpressCheckoutPayment call.
        """
        order_cls = get_order_class()
        self.order = order_cls.get_by_payment_details(
            {'token': response['TOKEN']}
        )
        if self.order is None or self.order.state is not OrderStates.created:
            return redirect(self.url_root + url_for('payment.error_payment',
                                    payment_method=self.method_name))

        request_params = {
            'METHOD': DO_PAYMENT,
            'TOKEN': response['TOKEN'],
            'PAYERID': response['PAYERID'],
            'PAYMENTREQUEST_0_AMT': self.order.total_price,
            'PAYMENTREQUEST_0_PAYMENTACTION': ACTION,
            'PAYMENTREQUEST_0_CURRENCYCODE': CURRENCY,
        }

        response = self.__do_request(request_params)
        if response['ACK'] == RESPONSE_OK:
            self.order.set_payment_details(token=unicode(response))
            self.order.mark_paid()

            return redirect(self.url_root + url_for('payment.success_payment',
                                    payment_method=self.method_name))

        return redirect(self.url_root + url_for('payment.error_payment',
                                payment_method=self.method_name,
                                order_id=self.order.id))

    def __get_payment_details(self, token, PayerID):
        """ If the customer authorizes the payment, the customer is redirected
            to the return URL that you specified in the SetExpressCheckout
            call. The return URL is appended with the same token as the token
            used above.
        :type PayerID: basestring
        """
        request_params = {
            'METHOD': GET_CHECKOUT,
            'TOKEN': token,
        }

        response = self.__do_request(request_params)

        if response['ACK'] == RESPONSE_OK:
            return self.__capture_payment(response)

        return redirect(self.url_root + url_for('payment.error_payment',
                                payment_method=self.method_name))

    def init_payment(self, payment_details=None):
        """ Initialization payment process.
        """
        assert isinstance(payment_details, Mapping)
        return self.__set_checkout(self.order.total_price, payment_details)

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
