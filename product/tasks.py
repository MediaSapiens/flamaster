from datetime import datetime, timedelta

from flamaster.extensions import db
from flamaster.product.models import Shelf
from flamaster.product.utils import get_cart_class


def drop_unordered_cart_items():
    cart_cls = get_cart_class()
    expirity_marker = datetime.utcnow() - timedelta(minutes=20)
    expired_q = cart_cls.expired(expirity_marker)
    for cart in expired_q:
        Shelf.query.filter_by(price_option_id=cart.price_option_id).\
            update({'quantity': Shelf.quantity + cart.amount})
    response = expired_q.count()
    expired_q.delete()
    db.session.commit()
    return response
