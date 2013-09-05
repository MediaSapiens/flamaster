from .base import BasePaymentMethod
from flamaster.product.models import PaymentTransaction


class DirectDebitPaymentMethod(BasePaymentMethod):
    method_name = 'direct_debit'

    def process_payment(self, **kwargs):
        return PaymentTransaction.create(status=PaymentTransaction.ACCEPTED,
                                details='direct_debit: %s' % self.order_data.__str__())
