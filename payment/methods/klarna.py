from klarna.Klarna import add_transaction

from base import BasePaymentMethod


class KlarnaPaymentMethod(BasePaymentMethod):
    def init_payment(self, amount, currency, description):
        return add_transaction()
