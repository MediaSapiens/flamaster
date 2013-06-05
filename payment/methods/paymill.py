from __future__ import absolute_import

from flask import request, current_app

from flamaster.product.models import Country, PaymentTransaction

from .base import BasePaymentMethod

import pymill
import json


class PaymillPaymentMethod(BasePaymentMethod):
    method_name = 'paymill'

    def __init__(self, *args, **kwargs):
        super(PaymillPaymentMethod, self).__init__(*args, **kwargs)

        self.paymill = pymill.Pymill(self.settings['PRIVATE_KEY'])
        self.customer = None

        if self.order_data is not None:
            self.customer = self.order_data.get('customer')

    def init_payment(self):
        pass

    def process_payment(self, pno=None):
        data = json.loads(request.data)
        amount = int(self.order_data.get('total_price', 0) * 100)
        resp = self.paymill.transact(amount=amount, token=data['token'])
