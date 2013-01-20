from flamaster.account.models import Customer
from .models import Order


def new_order(customer_id, payment_method):
    customer = Customer.query.get_or_404(customer_id)
    billing_address = customer.billing_address
    delivery_address = customer.delivery_address or billing_address

    order = Order.create(customer, billing_address, delivery_address,
                         payment_method=payment_method,
                         delivery_method='eticket')
    return order
