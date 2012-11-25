import logging
from flask import render_template
from flamaster.account.models import Address, User

from . import product as bp
from .models import Order, Delivery


logger = logging.getLogger(__name__)
from .models import Order


@bp.route('/test_checkout/<method>/')
def test_checkout(method):
    if method == 'paypal':
        user = User.query.filter_by(email='test@example.com').first()
        address = Address.create(city='New York',
                                         street='70 Lincoln Center Plz',
                                         apartment='1',
                                         zip_code='626262')

        print user
        address = Address.create(city='New York',
                                 street='70 Lincoln Center Plz',
                                 apartment='1',
                                 zip_code='626262')
        customer = user.customer
        customer.billing_address = address
        customer.delivery_address = address
        customer.save()

        order = Order.create(customer=customer,
                             payment_method=method,
                             delivery_address=customer.delivery_address,
                             billing_address=customer.billing_address)

        payment_meth = order.resolve_payment()
        return payment_meth.init_payment(order.total_price + 1, 'USD')
    return render_template('test.html', method=method)
