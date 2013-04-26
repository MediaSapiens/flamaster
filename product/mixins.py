# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from flamaster.core import lazy_cascade
from flamaster.core.models import CRUDMixin
from flamaster.extensions import db
from flamaster.conf.settings import SHOP_ID

from flask import current_app

from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr

from werkzeug.utils import import_string

from . import OrderStates
from .signals import cart_created, cart_removed


class OrderMixin(CRUDMixin):
    shop_id = db.Column(db.String(128), default=SHOP_ID)

    billing_city = db.Column(db.Unicode(255))
    billing_street = db.Column(db.Unicode(255))
    billing_apartment = db.Column(db.Unicode(20))
    billing_zip_code = db.Column(db.String(20))

    delivery_city = db.Column(db.Unicode(255))
    delivery_street = db.Column(db.Unicode(255))
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
        """ This method should be overrided in Order model implemetation
        """
        raise NotImplementedError()

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
    def _prepare_address(cls, addr_type, address_instance):
        exclude_fields = ['customer_id', 'created_at', 'id']
        address_dict = address_instance.as_dict(exclude=exclude_fields)
        return dict(('{}_{}'.format(addr_type, key), value)
                    for key, value in address_dict.iteritems())

    @classmethod
    def _resolve_delivery(cls, delivery, address):
        return delivery.calculate_price(address)


class CartMixin(CRUDMixin):
    """ Cart record for concrete product
    """
    product_id = db.Column(db.String, nullable=False)
    product_variant_id = db.Column(db.String, nullable=False)
    price_option_id = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, default=0)  # amount of the same items
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
    def create(cls, commit=True, **kwargs):
        """ Cart creation method. Accepted params are:
        :param product: BaseProduct or it's subclass instance
        :param product_variant: instance of BaseProductVariant subclass
        :param price_option: instance of BasePriceOption subclass
        :param amount: amount of products to place in cart
        :param customer_id: instance of Customer model
        """
        instance_kwargs = {
            'product_id': str(kwargs['product'].id),
            'product_variant_id': str(kwargs['product_variant'].id),
            'price_option_id': str(kwargs['price_option'].id),
            'customer_id': kwargs['customer'].id,
            'amount': kwargs['amount'],
            'price': kwargs['product'].get_price(kwargs['price_option'].id,
                                                 kwargs['amount']),
        }
        instance = super(CartMixin, cls).create(**instance_kwargs)
        cart_created.send(current_app._get_current_object(),
                     price_option_id=kwargs['price_option'].id,
                     amount=kwargs['amount'])
        return instance

    def delete(self, commit=True):
        cart_removed.send(current_app._get_current_object(),
                          price_option_id=self.price_option_id,
                          amount=self.amount)
        return super(CartMixin, self).delete(commit)

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
