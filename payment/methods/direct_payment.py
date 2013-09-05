from .base import BasePaymentMethod
from flamaster.product.models import PaymentTransaction


class DirectPaymentMethod(BasePaymentMethod):
    method_name = 'direct_payment'

    def process_payment(self, **kwargs):
        return PaymentTransaction.create(status=PaymentTransaction.ACCEPTED,
                                details='direct_payment: %s' % self.order_data.__str__())
