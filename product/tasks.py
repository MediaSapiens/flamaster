from datetime import datetime, timedelta

from flask import current_app
from flask.ext.babel import lazy_gettext as _

from flamaster.core import db
from flamaster.core.utils import send_email
from flamaster.product.datastore import CartDatastore
from flamaster.product import OrderStates
from flamaster.product.models import (Cart, Shelf,
                                      PaymentTransaction, Order)

from werkzeug.utils import import_string


def drop_unordered_cart_items():
    expirity_marker = datetime.utcnow() - timedelta(minutes=20)
    expired_q = Cart.expired(expirity_marker)
    for cart in expired_q:
        Shelf.query.filter_by(price_option_id=cart.price_option_id).\
            update({'quantity': Shelf.quantity + cart.amount})
    response = expired_q.count()
    expired_q.delete()
    db.session.commit()
    return response


def check_pending_orders(payment_method):
    transactions = PaymentTransaction.query.filter_by(status=PaymentTransaction.PENDING)\
        .join(Order).filter(Order.payment_method == payment_method)
    conf = current_app.config['PAYMENT_METHODS'].get(payment_method)
    payment_module = import_string(conf.get('module'))
    goods_ds = CartDatastore(Cart)

    for transaction in transactions:
        mod = payment_module()
        result = mod.check_status(transaction)

        if result == PaymentTransaction.ACCEPTED:
            order = transaction.order
            goods_ds.mark_ordered(order.goods, order)
            order.mark_paid()
            send_email(_('Your order summary'), order.customer.email,
                       'order_created', **{'order': order, 'customer': order.customer})

        if result == PaymentTransaction.DENIED:
            order.update(state=OrderStates.provider_denied)
            send_email(_('Your order status'), order.customer,
                       'payment_denied', **{'order': order})

        transaction.update(status=result)

    db.session.commit()