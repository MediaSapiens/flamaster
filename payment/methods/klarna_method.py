from klarna import Klarna, Config

from .base import BasePaymentMethod


class KlarnaPaymentMethod(BasePaymentMethod):
    method_name = 'klarna'
    def __init__(self, *args, **kwargs):
        super(KlarnaPaymentMethod, self).__init__(*args, **kwargs)

        self.klarna = Klarna(Config(**self.settings))

    def init_payment(self):
        return self.klarna.add_transaction()
