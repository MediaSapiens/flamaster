# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t

from flamaster.account.models import Customer
from flamaster.core import lazy_cascade
from flamaster.core.models import CRUDMixin
from flamaster.extensions import db
from flamaster.conf.settings import SHOP_ID

from flask import current_app

from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr

from werkzeug.utils import import_string

from . import OrderStates
from .signals import order_created
from .utils import get_cart_class


groupon_details = t.Dict({
    'deal': t.Int,
    'voucher': t.String,
    'code': t.String
}).ignore_extra('*')


class OrderMixin(CRUDMixin):
    shop_id = db.Column(db.String(128), default=SHOP_ID)

    billing_city = db.Column(db.Unicode(255), nullable=False)
    billing_street = db.Column(db.Unicode(255), nullable=False)
    billing_apartment = db.Column(db.Unicode(20))
    billing_zip_code = db.Column(db.String(20))

    delivery_city = db.Column(db.Unicode(255), nullable=False)
    delivery_street = db.Column(db.Unicode(255), nullable=False)
    delivery_apartment = db.Column(db.Unicode(20))
    delivery_zip_code = db.Column(db.String(20))
    # summary cost of all cart items linked with this order
    goods_price = db.Column(db.Numeric(precision=18, scale=2))

    vat = db.Column(db.Numeric(precision=18, scale=2))
    total_price = db.Column(db.Numeric(precision=18, scale=2))

    payment_method = db.Column(db.String, nullable=False, index=True)
    state = db.Column(db.Integer, index=True)
    # stored cost for the order delivery
    delivery_method = db.Column(db.String, nullable=False, index=True)
    delivery_price = db.Column(db.Numeric(precision=18, scale=2))

    @declared_attr
    def billing_country_id(cls):
        return db.Column(db.Integer, db.ForeignKey('countries.id',
                         use_alter=True, name='fk_billing_country'))

    @declared_attr
    def delivery_country_id(cls):
        return db.Column(db.Integer, db.ForeignKey('countries.id',
                         use_alter=True, name='fk_delivery_country'))

    @declared_attr
    def customer_id(cls):
        return db.Column(db.Integer, db.ForeignKey('customers.id'),
                         nullable=False, index=True)

    @declared_attr
    def customer(cls):
        return db.relationship('Customer',
                               backref=db.backref('orders', **lazy_cascade))

    @declared_attr
    def goods(cls):
        return db.relationship('Cart', backref='order', **lazy_cascade)

    @classmethod
    def create_from_api(cls, customer_id, **kwargs):
        """ Create order instance from data came from the API
        """
        cart_cls = get_cart_class()
        customer = Customer.query.get_or_404(customer_id)

        billing_address = customer.billing_address
        delivery_address = customer.delivery_address or billing_address

        goods = cart_cls.for_customer(customer)
        goods_price = cart_cls.get_price(goods)

        details = kwargs.pop('payment_details')

        # delivery_price = cls.__resolve_delivery(kwargs['delivery'],
        #                                         delivery_address)

        # TODO: total_price = goods_price + delivery_price
        kwargs.update({
            'delivery_method': 'eticket',
            'customer': customer,
            'goods_price': goods_price,
            'total_price': goods_price,
            'state': OrderStates.created
        })

        kwargs.update(cls.__prepare_address('delivery', delivery_address))
        kwargs.update(cls.__prepare_address('billing', billing_address))

        instance = cls.create(**kwargs)
        # Attach cart items to order and mark as ordered
        cart_cls.mark_ordered(goods, instance)
        # Commit manipulation on goods
        db.session.commit()

        if kwargs['payment_method'] == 'groupon':
            instance.details = groupon_details.check(details)

        method = instance.resolve_payment()
        method.process_payment()
        # Send signal on order creation
        order_created.send(current_app._get_current_object(), order=instance)
        return instance

    def mark_paid(self):
        return self.update(state=OrderStates.paid)

    def resolve_payment(self, method=None):
        payment_method = self.payment_method or method
        method = current_app.config['PAYMENT_METHODS'][payment_method]
        class_string = method['module']
        PaymentMethod = import_string(class_string)
        return PaymentMethod(self)

    def set_payment_details(self, payment_details):
        raise NotImplementedError()

    @classmethod
    def get_by_payment_details(cls, payment_details):
        raise NotImplementedError("Payment Details: %s", payment_details)

    @classmethod
    def __prepare_address(cls, addr_type, address_instance):
        exclude_fields = ['customer_id', 'created_at', 'id']
        address_dict = address_instance.as_dict(exclude=exclude_fields)
        return dict(('{}_{}'.format(addr_type, key), value)
                    for key, value in address_dict.iteritems())

    @classmethod
    def __resolve_delivery(cls, delivery, address):
        return delivery.calculate_price()


class CartMixin(CRUDMixin):
    """ Cart record for concrete product
    """
    product_id = db.Column(db.String, nullable=False)
    product_variant_id = db.Column(db.String, nullable=False)
    price_option_id = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, default=0)
    price = db.Column(db.Numeric(precision=18, scale=2))
    is_ordered = db.Column(db.Boolean, default=False, index=True)

    @declared_attr
    def order_id(cls):
        return db.Column(db.Integer, db.ForeignKey('orders.id'))

    @declared_attr
    def customer_id(cls):
        return db.Column(db.Integer, db.ForeignKey('customers.id'),
                         nullable=False)

    @declared_attr
    def customer(cls):
        db.relationship('Customer',
                        backref=db.backref('carts', **lazy_cascade))

    @classmethod
    def create(cls, amount, customer, product, product_variant,
               price_option):
        """ Cart creation method. Accepted params are:
        :param product: BaseProduct or it's subclass instance
        :param product_variant: instance of BaseProductVariant subclass
        :param price_option: instance of BasePriceOption subclass
        :param amount: amount of products to place in cart
        :param customer_id: instance of Customer model
        """
        instance_kwargs = {
            'product_id': str(product.id),
            'product_variant_id': str(product_variant.id),
            'price_option_id': str(price_option.id),
            'price': product.get_price(price_option.id, amount),
            'customer_id': customer.id,
            'amount': amount
        }
        return super(CartMixin, cls).create(**instance_kwargs)

    # @classmethod
    # def for_seat_data(cls, price_option, )

    @classmethod
    def for_customer(cls, customer, is_ordered=False):
        """ helper method for obtaining cart records for concrete customer
        """
        return cls.query.filter_by(customer_id=customer.id,
                                   is_ordered=is_ordered)

    @classmethod
    def expired(cls, timedelta):
        """ Return all cart items unoredered within expected time period
            :param timedelta: datetime.datetime type for expirity marker
        """
        return cls.query.filter(cls.created_at < timedelta,
                                cls.is_ordered == False)

    @classmethod
    def get_price(cls, query):
        # return sum(map(attrgetter('price'), carts_query))
        return db.session.query(func.sum(cls.price)) \
            .filter(query._criterion).scalar()

    @classmethod
    def mark_ordered(cls, carts_query, order):
        assert isinstance(order, OrderMixin)
        return carts_query.update({'is_ordered': True, 'order_id': order.id})
