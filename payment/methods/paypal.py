# -*- encoding: utf-8 -*-
import logging
import requests
from flask import redirect, url_for, request
from urlparse import parse_qs

from .base import BasePaymentMethod



ACTION = 'SELL'
SET_CHECKOUT = 'SetExpressCheckout'
GET_CHECKOUT = 'GetExpressCheckoutDetails'
DO_PAYMENT = 'DoExpressCheckoutPayment'
RESPONSE_OK = 'Success'
logger = logging.getLogger(__name__)


class PayPalPaymentMethod(BasePaymentMethod):
    """ PayPal API handler. Designed to use only express checkout methods.
        See https://www.x.com/developers/paypal/documentation-tools/express-checkout/how-to/ht_ec-singleItemPayment-curl-etc

        Collecting a one-time payment with PayPal requires:

            Setting up the payment information.
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
        return parse_qs(resp.text)

    def __set_checkout(self, amount, currency):
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
            'PAYMENTREQUEST_0_CURRENCYCODE': currency,
            # FIXME: BuildError
            'RETURNURL': request.url_root.rstrip('/') + url_for(
                                            'payment.process_payment',
                                            payment_method=self.method_name),
            'CANCELURL': request.url_root.rstrip('/') + url_for(
                                            'payment.cancel_payment',
                                            payment_method=self.method_name)
        }
        response = self.__do_request(request_params)

        if response['ACK'][0] == RESPONSE_OK:
            self.order.set_payment_details(response['TOKEN'])
            webface_url = self.__get_redirect_url(response)
            return redirect(webface_url)
        return redirect(url_for('payment.error_payment',
                                payment_method=self.method_name))

    def __obtain_authorized_payment_details(self, token):
        """ If the customer authorizes the payment, the customer is redirected
            to the return URL that you specified in the SetExpressCheckout
            call. The return URL is appended with the same token as the token
            used above.
        """
        request_params = {
            'METHOD': DO_PAYMENT,
            'TOKEN': token,
        }
        response = self.__do_request(request_params)
        if response['ACK'][0] == RESPONSE_OK:
            return self.__capture_the_payment(token=token,
                    payer_id=response.json['PAYERID'])
        logger.debug("get checkout err: %s", response)
        return redirect(url_for('payment.error_payment'))

    def __capture_the_payment(self, token, payer_id):
        """ Final step. The payment can be captured (collected) using the
            DoExpressCheckoutPayment call.
        """
        request_params = {
                'METHOD': GET_CHECKOUT,
                'TOKEN': token,
                'PAYERID': payer_id
        }
        response = self.__do_request(request_params)
        if response['ACK'][0] == RESPONSE_OK:
            self.order.get_by_payment_details(response['TOKEN'])
            self.order.set_payment_details(' '.join(response))
            return self.order.mark_paid()
        logger.debug("get checkout err: %s", response)

    def init_payment(self, amount, currency):
        """ Initialization payment process.
        """
        return self.__set_checkout(amount, currency)

    def process_payment(self):
        token = request.args['TOKEN']
        return self.__obtain_authorized_payment_details(token)

    def __get_redirect_url(self, response):
        face = "https://www.{}paypal.com/webscr?cmd=_express-checkout&token={}"
        return face.format(self.sandbox and 'sandbox.' or '',
                           response['TOKEN'][0])

    @property
    def endpoint(self):
        endpoint_args = (self.settings['SIGNATURE'] and '-3t' or '',
                         self.sandbox and 'sandbox.' or '',)
        return 'https://api{}.{}paypal.com/nvp'.format(*endpoint_args)
