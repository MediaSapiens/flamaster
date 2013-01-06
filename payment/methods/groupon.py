# -*- encoding: utf-8 -*-
from flamaster.core.utils import jsonify_status_code
from .base import BasePaymentMethod


class GrouponPaymentMethod(BasePaymentMethod):
    method_name = 'groupon'

    def init_payment(self):  # amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError

    def verify(self, data):
        return jsonify_status_code({'message': 'OK', 'seats': 4})
