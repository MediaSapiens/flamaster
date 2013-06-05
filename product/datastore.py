from __future__ import absolute_import

from flamaster.core import db
from flamaster.core.datastore import AbstractDatastore
from flamaster.core.utils import round_decimal

from operator import attrgetter

from . import OrderStates
from .signals import order_created

import uuid


class OrderDatastore(AbstractDatastore):
    """ Class for manipulations with order model state
    """
    def __init__(self, order_model, cart_model, customer_model, transaction_model):
        self.order_model = order_model
        self.goods_ds = CartDatastore(cart_model)
        self.customer_model = customer_model
        self.transaction_model = transaction_model
        self.transaction_ds = PaymentTransactionDatastore(transaction_model, cart_model)

    def find_one(self, **kwargs):
        return self.find(**kwargs).first()

    def find(self, **kwargs):
        return self.order_model.query.filter_by(**kwargs)

    def __collect_data(self, customer_id, **kwargs):
        """ Create order instance from data came from the API
        """
        customer = self.customer_model.query.get_or_404(customer_id)
        delivery_address = customer.delivery_address
        billing_address = customer.billing_address or delivery_address

        goods = self.goods_ds.find(customer=customer, is_ordered=False)
        goods_price = self.goods_ds.get_price(goods)
        delivery_price = self.order_model.resolve_delivery(kwargs.pop('delivery_provider_id'),
                                                           goods,
                                                           delivery_address)
        payment_fee = self.order_model.resolve_payment_fee(kwargs['payment_method'],
                                                           goods_price)
        total_price = round_decimal(goods_price + delivery_price + payment_fee)

        kwargs.update({
            'reference': str(uuid.uuid4().node),
            'delivery_method': 'provider',
            'customer': customer,
            'goods_price': goods_price,
            'payment_fee': payment_fee,
            'total_price': total_price,
            'delivery_price': delivery_price,
            'state': OrderStates.created
        })

        kwargs.update(self.__prepare_address('delivery', delivery_address))
        kwargs.update(self.__prepare_address('billing', billing_address))

        return goods, kwargs

    def create_from_api(self, customer_id, **kwargs):
        """ Create order instance from data came from the API
        """
        goods, kwargs = self.__collect_data(customer_id, **kwargs)

        method = self.order_model.resolve_payment(goods=goods, order_data=kwargs)
        tnx = method.process_payment()

        order = self.order_model.create(**kwargs)

        self.transaction_ds.process(tnx, order, goods)
        # Commit manipulation on goods
        db.session.commit()

        # Send signal on order creation
        order_created.send(order)
        return order

    def create_from_request(self, customer_id, **kwargs):
        """ Create order instance from data came from the API
        """
        goods, kwargs = self.__collect_data(customer_id, **kwargs)

        method = self.order_model.resolve_payment(goods=goods, order_data=kwargs)
        return method.init_payment()

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
        return round_decimal(sum(map(attrgetter('price'), carts_query)))

    def mark_ordered(self, carts_query, order):
        return carts_query.update({'is_ordered': True, 'order_id': order.id})


class PaymentTransactionDatastore(AbstractDatastore):

    def __init__(self, transaction_model, cart_model):
        self.transaction_model = transaction_model
        self.goods_ds = CartDatastore(cart_model)

    def process(self, tnx, order, goods):
        tnx.update(order_id=order.id)

        if tnx.status == tnx.ACCEPTED:
            # Attach cart items to order and mark as ordered
            self.goods_ds.mark_ordered(goods, order)
            order.mark_paid()
