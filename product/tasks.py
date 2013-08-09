from __future__ import absolute_import
from datetime import datetime, timedelta

from flamaster.extensions import db

from .models import Shelf
from .utils import get_cart_class
from .signals import carts_removed


def drop_unordered_cart_items():
    cart_cls = get_cart_class()
    expirity_marker = datetime.utcnow() - timedelta(minutes=20)
    expired_q = cart_cls.expired(expirity_marker)
    for cart in expired_q:
        Shelf.query.filter_by(price_option_id=cart.price_option_id).\
            update({'quantity': Shelf.quantity + cart.amount})
        # TODO: need to implement cartSession entity to massively remove
        # stalled ones.
        related = cart_cls.for_customer(cart.customer)
        related.delete()
    response = expired_q.count()
    carts_removed.send(
        response,
        carts=[cart.id for cart in expired_q]
    )
    expired_q.delete()
    db.session.commit()
    return response
