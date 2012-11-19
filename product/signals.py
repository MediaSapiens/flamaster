# -*- coding: utf-8 -*-
from flask.ext.mail import Message
from operator import attrgetter
from sqlalchemy import event
# from flamaster.account.models import User
from . import mail, db
from .documents import price_created, price_updated, price_deleted
from .models import Order, Shelf


# @user_registered.connect
# def create_customer_for_newcommer(sender, app):
#     sender['user'].customer = Customer()


@price_created.connect
def put_on_shelf(price_option):
    """ Putting newly created priced item on shelf
    """
    Shelf.create(price_option_id=str(price_option.id),
                 quantity=price_option.quantity)


@price_updated.connect
def update_on_shelf(price_option):
    Shelf.query.update(quantity=price_option.quantity) \
                .where(price_option_id=price_option.id)
    db.session.commit()


@price_deleted.connect
def remove_from_shelf(price_option):
    Shelf.query.delete().where(price_option_id=price_option.id)
    db.session.commit()


def order_creation_sender(mapper, connection, instance):
    owners = list(set(map(attrgetter('product.created_by'), instance.goods)))

    with mail.connect() as conn:
        for owner in owners:
            conn.send(Message(
                recipients=[owner],
                subject="New order #{0.id}".format(instance),
                body="{} ordered ...".format(instance.customer)
            ))

        conn.send(Message(
            recipients=[instance.customer.email],
            subject="Your order #{0.id}".format(instance),
            body="Thank you for ordering"
        ))

event.listen(Order, 'after_insert', order_creation_sender)

# after_insert(cls, mapper=None, connection=None, instance=None):
# ins = cls.index_table.insert().values(**cls.get_values(instance))
# cls.execute(ins)
