# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from blinker import Namespace

# from flamaster.account.models import User
from flask import current_app
from flamaster.extensions import db
from .models import Shelf


logger = logging.getLogger(__name__)
signals = Namespace()

price_created = signals.signal('price_created')
price_updated = signals.signal('price_updated')
price_deleted = signals.signal('price_deleted')

order_created = signals.signal('order-created')
# @user_registered.connect
# def create_customer_for_newcommer(sender, app):
#     sender['user'].customer = Customer()


@price_created.connect
def put_on_shelf(sender, price_option):
    """ Putting newly created priced item on shelf
    """
    Shelf.create(price_option_id=str(price_option.id),
                 quantity=price_option.quantity)


@price_updated.connect
def update_on_shelf(price_option):
    Shelf.query.filter_by(price_option_id=str(price_option.id))\
        .update({'quantity': price_option.quantity})
    db.session.commit()


@price_deleted.connect
def remove_from_shelf(price_option):
    Shelf.query.delete().where(price_option_id=price_option.id)
    db.session.commit()


@order_created.connect
def on_order_created(sender, order):
    for cart_item in order.goods:
        shelves = Shelf.get_by_price_option(
                    price_option_id=cart_item.price_option_id)
        if shelves.first() is None:
            current_app.logger.error('Item is not on shelf %s',
                                     cart_item.price_option_id)
        else:
            shelves.update({'sold': Shelf.sold + 1})
        db.session.commit()

#def order_creation_sender(mapper, connection, instance):
#    owners = list(set(map(attrgetter('product.created_by'), instance.goods)))

#    with mail.connect() as conn:
#        for owner in owners:
#            conn.send(Message(
#                recipients=[owner],
#                subject="New order #{0.id}".format(instance),
#                body="{} ordered ...".format(instance.customer)
#            ))
#
#        logger.debug(dir(instance)),
#        logger.debug(instance),
#        conn.send(Message(
#            recipients=[instance.customer.email],
#            subject="Your order #{0.id}".format(instance),
#            body="Thank you for ordering"
#        ))

#event.listen(Order, 'after_insert', order_creation_sender)

# after_insert(cls, mapper=None, connection=None, instance=None):
# ins = cls.index_table.insert().values(**cls.get_values(instance))
# cls.execute(ins)
