from .base import BasePaymentMethod
from flamaster.product.models import PaymentTransaction


class CashPaymentMethod(BasePaymentMethod):
    method_name = 'cash'

    def process_payment(self, **kwargs):
        return PaymentTransaction.create(status=PaymentTransaction.ACCEPTED,
                                details='cash: %s' % self.order_data.__str__())
