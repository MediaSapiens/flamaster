from __future__ import absolute_import
from datetime import datetime, timedelta

from flamaster.extensions import db

from .models import Shelf
from .utils import get_cart_class, get_order_class
from .signals import carts_removed


def drop_unordered_cart_items():
    cart_cls = get_cart_class()
    expirity_marker = datetime.utcnow() - timedelta(minutes=20)
    expired_carts = cart_cls.expired(expirity_marker)

    for cart in expired_carts:
        Shelf.query.filter_by(price_option_id=cart.price_option_id).\
            update({'quantity': Shelf.quantity + cart.amount})
        # TODO: need to implement cartSession entity to massively remove
        # stalled ones.
        if cart.customer is not None:
            related = cart_cls.for_customer(cart.customer)
            related.delete()
    response = expired_carts.count()
    carts_removed.send(
        response,
        carts=[cart.id for cart in expired_carts]
    )
    expired_carts.delete()
    db.session.commit()
    return response


def drop_unpaid_order_items():
    order_cls = get_order_class()
    expired_orders = order_cls.expired(max_age=timedelta(minutes=10))

    for order in expired_orders:
        order.cancel_by_merchant()
