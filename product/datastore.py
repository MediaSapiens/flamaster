from __future__ import absolute_import
from flask import current_app
from flamaster.core import db
from flamaster.core.datastore import AbstractDatastore

from operator import attrgetter

from . import OrderStates
from .signals import order_created

import uuid


class OrderDatastore(AbstractDatastore):
    """ Class for manipulations with order model state
    """
    def __init__(self, order_model, cart_model, customer_model):
        self.order_model = order_model
        self.goods_ds = CartDatastore(cart_model)
        self.customer_model = customer_model

    def find_one(self, **kwargs):
        return self.find(**kwargs).first()

    def find(self, **kwargs):
        return self.order_model.query.filter_by(**kwargs)

    def create_from_api(self, customer_id, **kwargs):
        """ Create order instance from data came from the API
        """
        customer = self.customer_model.query.get_or_404(customer_id)
        billing_address = customer.billing_address
        delivery_address = customer.delivery_address or billing_address

        goods = self.goods_ds.find(customer=customer)
        goods_price = self.goods_ds.get_price(goods)
        # delivery_price = cls.__resolve_delivery(kwargs['delivery'],
        #                                         delivery_address)

        # TODO: total_price = goods_price + delivery_price
        kwargs.update({
            'reference': str(uuid.uuid4().node),
            'delivery_method': 'eticket',
            'customer': customer,
            'goods_price': goods_price,
            'total_price': goods_price,
            'state': OrderStates.created
        })

        kwargs.update(self.__prepare_address('delivery', delivery_address))
        kwargs.update(self.__prepare_address('billing', billing_address))

        order = self.order_model.create(**kwargs)
        # Attach cart items to order and mark as ordered
        #self.goods_ds.mark_ordered(goods, order)
        # Commit manipulation on goods
        db.session.commit()

        method = order.resolve_payment()
        method.process_payment()
        # Send signal on order creation
        order_created.send(current_app._get_current_object(), order=order)
        return order

    def __prepare_address(self, addr_type, address_instance):
        exclude_fields = ['customer_id', 'created_at', 'id']
        address_dict = address_instance.as_dict(exclude=exclude_fields)
        return dict(('{}_{}'.format(addr_type, key), value)
                    for key, value in address_dict.iteritems())


class CartDatastore(AbstractDatastore):

    def __init__(self, cart_model):
        self.cart_model = cart_model

    def find_one(self, **kwargs):
        return self.find_many(**kwargs).first()

    def find(self, **kwargs):
        return self.cart_model.query.filter_by(**kwargs)

    def get_price(self, carts_query):
        return sum(map(attrgetter('price'), carts_query))

    def mark_ordered(self, carts_query, order):
        return carts_query.update({'is_ordered': True, 'order_id': order.id})
