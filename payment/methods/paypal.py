# -*- encoding: utf-8 -*-
import logging
import requests
from flask import redirect, render_template
from urlparse import parse_qs

from .base import BasePaymentMethod
from .. import payment


ACTION = 'SELL'
SET_CHECKOUT = 'SetExpressCheckout'
GET_CHECKOUT = 'GetExpressCheckoutDetails'
DO_PAYMENT = 'DoExpressCheckoutPayment'
RESPONSE_OK = 'Success'
PAYMENT_METHOD = 'PAYPAL'
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
    # Must be uppercased
    method_name = 'PAYPAL'

    def __do_request(self, request_params):
        """ Directly request
        """
        payload = self.settings['payload']
        request_params.update(payload)
        logger.debug(self.__endpoint)
        logger.debug(self.__endpoint)
        resp = requests.get(self.__endpoint, params=request_params)
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
            'returnUrl': '',
            'cancelUrl': '',
        }
        response = self.__do_request(request_params)

        if response['ACK'] == RESPONSE_OK:
            self.order.set_payment_details(response['TOKEN'])
            webface_url = self.__prepare_redirect_url(response)
            return redirect(webface_url)
        else:
            logger.debug("set checkout err: %s", response)

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
        if response['ACK'] == RESPONSE_OK:
            return self.__capture_the_payment(token=token,
                    payer_id=response.json['PAYERID'])
        logger.debug("get checkout err: %s", response)

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
        if response['ACK'] == RESPONSE_OK:
            self.order.get_by_payment_details(response['TOKEN'])
            self.order.set_payment_details(' '.join(response))
            return self.order.mark_paid()
        logger.debug("get checkout err: %s", response)

    def init_payment(self, amount, currency):
        """ Initialization payment process.
        """
        self.__set_checkout(amount, currency)

    def process_payment(self, token):
        return self.__obtain_authorized_payment_details(token)

    def __prepare_redirect_url(self, response):
        face = "https://{}paypal.com/webscr?cmd=_express-checkout&token={}"
        return face.format(
                self.settings['SANDBOX'] and 'sandbox.',
                response.json['token'])

    @property
    def __endpoint(self):
        endpoint_args = (self.settings['payload']['SIGNATURE'] and '-3t' or '',
                self.settings['SANDBOX'] and 'sandbox.' or '',)
        return 'https://api{}.{}paypal.com/nvp'.format(*endpoint_args)


@payment.route('/paypal/process/<string:token>', methods=['POST',])
def dispatch_request(self, token):
    order_data = PayPalPaymentMethod().process_payment(token)
    return render_template('success_order.html', order=order_data)


#payment.add_url_rule('/initialization',
#        view_func=InitPaymentView.as_view('init_payment'))
#payment.add_url_rule('/process',
#        view_func=ProcessPaymentView.as_view('process_payment'))
