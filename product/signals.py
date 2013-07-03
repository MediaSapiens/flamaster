# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from blinker import Namespace

from flask import current_app
from flamaster.extensions import db

from .models import Shelf


__all__ = [
    'price_created', 'price_updated', 'price_deleted',
    'order_created', 'order_paid',
    'cart_created', 'carts_removed', 'cart_removed'
]

logger = logging.getLogger(__name__)
signals = Namespace()

price_created = signals.signal('price_created')
price_updated = signals.signal('price_updated')
price_deleted = signals.signal('price_deleted')

order_created = signals.signal('order-created')
order_paid = signals.signal('order-paid')
cart_created = signals.signal('cart-created')
cart_removed = signals.signal('cart-removed')
carts_removed = signals.signal('carts-removed')
# @user_registered.connect
# def create_customer_for_newcommer(sender, app):
#     sender['user'].customer = Customer()


@price_created.connect
def put_on_shelf(sender, price_option_id, quantity):
    """ Putting newly created priced item on shelf
    """
    Shelf.create(price_option_id=str(price_option_id), quantity=quantity)


@price_updated.connect
def update_on_shelf(price_option):
    Shelf.query.filter_by(price_option_id=str(price_option.id)) \
        .update({'quantity': price_option.quantity})
    db.session.commit()


@price_deleted.connect
def remove_from_shelf(sender, price_option_id):
    shelf = Shelf.query.filter_by(price_option_id=str(price_option_id)).first()
    if shelf is not None:
        shelf.delete()


@order_paid.connect
def update_sold_on_shelf(sender, order):
    def update_sold_count(item):
        price_option_id, amount = item
        shelves = Shelf.get_by_price_option(price_option_id)
        if shelves.first() is None:
            message = 'Item {} is not on shelf or depleeted'.format(
                price_option_id)
            current_app.logger.error(message)
        else:
            shelves.update({'sold': Shelf.sold + amount})

    def aggregator(accumulator, item):
        if item.price_option_id in accumulator:
            accumulator[item.price_option_id] += item.amount
        else:
            accumulator[item.price_option_id] = item.amount
        return accumulator

    aggregate = reduce(aggregator, order.goods, {})
    map(update_sold_count, aggregate.items())

    db.session.commit()


@cart_created.connect
def on_cart_created(sender, price_option_id, amount):
    """ Synchronizing shelf state with amount added to cart

    :param sender: current app
    :param price_option_id: Price option to search shelf with
    :param amount: Amount of items to record
    """
    shelves = Shelf.get_by_price_option(price_option_id)
    if shelves.count() == 0:
        message = 'Item {} is not on shelf or depleeted'.format(price_option_id)
        current_app.logger.error(message)
    else:
        shelves.update({'sold': Shelf.sold + amount})
    db.session.commit()


@cart_removed.connect
def on_cart_removed(sender, price_option_id, amount):
    shelves = Shelf.get_by_price_option(price_option_id)
    if shelves.count() == 0:
        message = 'Item {} is not on shelf or depleeted'.format(price_option_id)
        current_app.logger.error(message)
    else:
        shelves.update({'sold': Shelf.sold - amount})

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
