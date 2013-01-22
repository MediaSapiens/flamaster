from flask import current_app
from flask.signals import Namespace
from operator import attrgetter

from . import db, OrderStates

signals = Namespace()
order_created = signals.signal('order-created')


class OrderDatastore(object):
    """ Class for manipulations with order model state
    """
    def __init__(self, order_model, cart_model, customer_model):
        self.order_model = order_model
        self.cart_model = cart_model
        self.customer_model = customer_model

    def find_order(self, **kwargs):
        return self.order_model.query.filter_by(**kwargs).first()

    def find_orders(self, **kwargs):
        return self.order_model.query.filter_by(**kwargs)

    def create_from_api(self, customer_id, **kwargs):
        """ Create order instance from data came from the API
        """
        customer = self.customer_model.query.get_or_404(customer_id)
        billing_address = customer.billing_address
        delivery_address = customer.delivery_address or billing_address

        goods = self.cart_model.for_customer(customer)
        # delivery_price = cls.__resolve_delivery(kwargs['delivery'],
        #                                         delivery_address)
        goods_price = sum(map(attrgetter('price'), goods)),
        # TODO: total_price = goods_price + delivery_price
        kwargs.update({
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
        goods.update({'is_ordered': True, 'order_id': order.id})
        # Commit manipulation on goods
        db.session.commit()
        order_created.send(current_app._get_current_object(), order=order)
        return order

    def __prepare_address(self, addr_type, address_instance):
        exclude_fields = ['customer_id', 'created_at', 'id']
        address_dict = address_instance.as_dict(exclude=exclude_fields)
        return dict(('{}_{}'.format(addr_type, key), value)
                    for key, value in address_dict.iteritems())
