# -*- encoding: utf-8 -*-
import logging
import requests
from flask import redirect, url_for, request, json, Response
from urlparse import parse_qsl

from flask import current_app

from flamaster.product import Order

from .base import BasePaymentMethod


CURRENCY = 'USD'
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
        # current_app.logger.debug('args: %s', dir(resp.request))
        current_app.logger.debug('args: %s', resp.request.full_url)
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

        current_app.logger.debug('SET CHECK: %s', response)

        if response['ACK'] == RESPONSE_OK:
            self.order.set_payment_details(response['TOKEN'])
            webface_url = self.__get_redirect_url(response)
            current_app.logger.debug('redirect url: %s', webface_url)
            return redirect(webface_url)

        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name))

    def __capture_payment(self, response):
        """ Final step. The payment can be captured (collected) using the
            DoExpressCheckoutPayment call.
        """
        self.order = Order.get_by_payment_details(response['TOKEN'])
        if self.order is None:
            return redirect(url_for('payment.error_payment',
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
        current_app.logger.debug('DO PAYMENT response: %s', response)
        if response['ACK'] == RESPONSE_OK:
            self.order.set_payment_details(unicode(response))
            self.order.mark_paid()

            return Response(response=json.dumps(response), status=201,
                    mimetype='application/json')

        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name,
                                order_id=self.order.id))

    def __get_payment_details(self, token, PayerID):
        """ If the customer authorizes the payment, the customer is redirected
            to the return URL that you specified in the SetExpressCheckout
            call. The return URL is appended with the same token as the token
            used above.
        """
        request_params = {
            'METHOD': GET_CHECKOUT,
            'TOKEN': token,
        }

        response = self.__do_request(request_params)
        current_app.logger.debug("get checkout: %s", response)

        if response['ACK'] == RESPONSE_OK:
            return self.__capture_payment(response)

        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name))

    def init_payment(self):
        """ Initialization payment process.
        """
        return self.__set_checkout(self.order.total_price)

    def process_payment(self):
        current_app.logger.debug("PP redirect: %s", request.args)
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
