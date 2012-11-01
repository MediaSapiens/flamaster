# -*- coding: utf-8 -*-
from flask.ext.mail import Message
from flask.ext.security import user_registered
from operator import attrgetter
from sqlalchemy import event
# from flamaster.account.models import User
from . import mail
from .models import Order, Customer


@user_registered.connect
def create_customer_for_newcommer(sender, app):
    sender['user'].customer = Customer()


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
