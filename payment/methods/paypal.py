# -*- encoding: utf-8 -*-
import logging
import requests
from flask import redirect, request
from flask.views import View
from urlparse import parse_qs

from .base import BasePaymentMethod
from . import bp
from flamaster.product.models import Order


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
#        url_endpoint = self.settings['endpoint']
        request_params.update(self.settings['payload'])
        # or self.endpoint
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
            'returnUrl': '',
            'cancelUrl': '',
        }
        response = self.__do_request(request_params)

        if response['ACK'] == RESPONSE_OK:
            self.__store_token(response['TOKEN'])
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
            'METHOD': GET_CHECKOUT,
            'TOKEN': token,
        }
        response = self.__do_request(request_params)
        if response['ACK'] == RESPONSE_OK:
            return self.__capture_the_payment(token=token,
                    payer_id=response['PAYERID'])
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
            order = self.__restore_order(response['TOKEN'])
            order.update(payment_details = ' '.join(response))
            return order.save()
        logger.debug("get checkout err: %s", response)

    def init_payment(self, amount, currency):
        """ Initialization payment process.
        """
        self.__set_checkout(amount, currency)

    def process_payment(self, token):
        return self.__obtain_authorized_payment_details(token)

    def __store_token(self, token):
        return self.order.update(payment_details = token)

    def __restore_order(self, token):
        return self.order.query.filter_by(payment_details=token).first()

    def __prepare_redirect_url(self, response):
        redirect_tpl = "{}?cmd=_express-checkout&token={}"
        return redirect_tpl.format(self.settings['webface'], self.ec_token)


class InitPaymentView(View):
    def dispatch_request(self):
        amount = request.json.get('amount')
        currency = request.json.get('currency')
        order = Order.create(customer_id=request.json.get('customer_id'))

        return PayPalPaymentMethod(order).init_payment(amount, currency)


class ProcessPaymentView(View):
    def dispatch_request(self):
        token = request.json.get('TOKEN')
        return PayPalPaymentMethod().process_payment(token)


bp.add_url_rule('/initialization', view_func=InitPaymentView.as_view())
bp.add_url_rule('/process', view_func=ProcessPaymentView.as_view())
