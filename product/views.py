import logging
from flask import render_template
from flamaster.account.models import Address, User

from . import product as bp
from .models import Order
from flamaster.conf.settings import DELIVERY_OPTIONS


logger = logging.getLogger(__name__)


@bp.route('/test_checkout/<method>/')
def test_checkout(method):
    if method == 'paypal':
        user = User.query.filter_by(email='test@example.com').first()
        address = Address.create(city='New York',
                                         street='70 Lincoln Center Plz',
                                         apartment='1',
                                         zip_code='626262')

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
                             delivery_method = DELIVERY_OPTIONS.keys()[0],
                             delivery_address=customer.delivery_address,
                             billing_address=customer.billing_address)
        order.total_price = 12.5
        order.save()

        payment_meth = order.resolve_payment(method)
        return payment_meth.init_payment()
    return render_template('test.html', method=method)
