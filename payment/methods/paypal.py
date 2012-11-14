# -*- encoding: utf-8 -*-
import logging
import requests
from flask import redirect
from flask.views import View
from urlparse import parse_qs
from .base import BasePaymentMethod


ACTION = 'SELL'
SET_CHECKOUT = 'SetExpressCheckout'
GET_CHECKOUT = 'GetExpressCheckoutDetails'
DO_PAYMENT = 'DoExpressCheckoutPayment'
RESPONSE_OK = 'Success'
logger = logging.getLogger(__name__)


class PayPalPaymentMethod(BasePaymentMethod):
    method_name = 'paypal'

    def __do_request(self, request_params):
        url_endpoint = self.settings['endpoint']
        request_params.update(self.settings['settings'])
        resp = requests.get(url_endpoint, params=request_params)
        return parse_qs(resp.text)

    def __set_checkout(self, amount, currency):
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
            self.ec_token = response['TOKEN']
            webface_url = self.__prepare_redirect_url(response)
            return redirect(webface_url)
        else:
            logger.debug("set checkout err: %s", response)

    def __get_details(self, token):
        request_params = {
            'METHOD': GET_CHECKOUT,
            'TOKEN': self.ec_token,
        }
        response = self.__do_request(request_params)
        if response['ACK'] == RESPONSE_OK:
            self.payer_id = response['PAYERID']
        else:
            logger.debug("get checkout err: %s", response)

    def __prepare_redirect_url(self, response):
        redirect_tpl = "{}?cmd=_express-checkout&token={}"
        return redirect_tpl.format(self.settings['webface'], self.ec_token)

    def process_payment(self, amount, currency, description):
        self.__set_checkout(amount, currency)




