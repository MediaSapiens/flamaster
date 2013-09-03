from .base import BasePaymentMethod
from flamaster.product.models import PaymentTransaction


class BankTransferPaymentMethod(BasePaymentMethod):
    method_name = 'bank_transfer'

    def process_payment(self, **kwargs):
        return PaymentTransaction.create(status=PaymentTransaction.ACCEPTED,
                                details='bank_transfer: %s' % self.order_data.__str__())
