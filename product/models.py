# -*- encoding: utf-8 -*-
from flask import current_app
from operator import attrgetter

from flamaster.account.models import Address

from flamaster.core import COUNTRY_CHOICES, lazy_cascade
from flamaster.core.models import CRUDMixin, TreeNode, NodeMetaClass
from flamaster.core.utils import resolve_class

from . import db


__all__ = ['Cart', 'Category', 'Delivery', 'Favorite', 'Order', 'Shelf']


class Cart(db.Model, CRUDMixin):
    """ Cart record for concrete product
    """
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.String, nullable=False)
    product_variant_id = db.Column(db.String, nullable=False)
    price_option_id = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(precision=18, scale=2))
    is_ordered = db.Column(db.Boolean, default=False, index=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    customer = db.relationship('Customer',
                               backref=db.backref('carts', **lazy_cascade))

    @classmethod
    def create(cls, amount, customer_id, product, product_variant,
               price_option):
        """ Cart creation method. Accepted params are:
        :param product: BaseProduct or it's subclass instance
        :param product_variant: instance of BaseProductVariant subclass
        :param price_option: instance of BasePriceOption subclass
        :param amount: amount of products to place in cart
        :param customer_id: instance of Customer model
        """
        price = product.get_price(price_option.id, amount)

        instance_kwargs = {
            'product_id': str(product.id),
            'product_variant_id': str(product_variant.id),
            'price_option_id': str(price_option.id),
            'price': price,
            'customer_id': customer_id
        }
        return super(Cart, cls).create(**instance_kwargs)

    @classmethod
    def for_customer(cls, customer_id):
        """ helper method for obtaining cart records for concrete customer
        """
        return cls.query.filter_by(customer_id=customer_id, is_ordered=False)


class Category(db.Model, TreeNode):
    """ Product category mixin
    """
    __metaclass__ = NodeMetaClass
    __mp_manager__ = 'mp'

    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return "{1}: <{0.id}, '{0.name}', {0.mp_depth}>".format(self,
            self.__class__.__name__)


class Country(db.Model, CRUDMixin):
    """ Model holding countries list """
    api_fields = ['id', 'short', 'name']

    short = db.Column(db.Unicode(3), nullable=False, index=True)

    @property
    def name(self):
        return COUNTRY_CHOICES[self.short]


class Favorite(db.Model, CRUDMixin):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                        ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('favorites',
                                                      lazy='dynamic'))
    product_id = db.Column(db.String(255), index=True)


class Order(db.Model, CRUDMixin):
    """ Model to keep ordered goods
    """
    payment_method = db.Column(db.String, nullable=False, index=True)
    billing_country_id = db.Column(db.Integer, db.ForeignKey('countries.id',
                                    use_alter=True, name='fk_billing_country'))
    billing_city = db.Column(db.Unicode(255), nullable=False)
    billing_street = db.Column(db.Unicode(255), nullable=False)
    billing_apartment = db.Column(db.Unicode(20))
    billing_zip_code = db.Column(db.String(20))
    delivery_country_id = db.Column(db.Integer, db.ForeignKey('countries.id',
                                use_alter=True, name='fk_delivery_country'))
    delivery_city = db.Column(db.Unicode(255), nullable=False)
    delivery_street = db.Column(db.Unicode(255), nullable=False)
    delivery_apartment = db.Column(db.Unicode(20))
    delivery_zip_code = db.Column(db.String(20))
    # summary cost of all cart items linked with this order
    goods_price = db.Column(db.Numeric(precision=18, scale=2))
    # stored cost for the order delivery
    delivery_cost = db.Column(db.Numeric(precision=18, scale=2))
    vat = db.Column(db.Numeric(precision=18, scale=2))
    total_cost = db.Column(db.Numeric(precision=18, scale=2))
    payment_details = db.Column(db.Unicode(255), unique=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    paid = db.Column(db.Boolean, default=False)
    customer = db.relationship('Customer',
                               backref=db.backref('orders', **lazy_cascade))

    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'))
    delivery = db.relationship('Delivery',
                               backref=db.backref('orders', **lazy_cascade))

    goods = db.relationship('Cart', backref='order', **lazy_cascade)

    @classmethod
    def create(cls, commit=True, **kwargs):
        """ Order creation method. Accepted params are:
        :param customer_id: int value for Customer id instance
        :param delivery_id: int value for Delivery id instance
        :param payment_method: int value for Payment id instance
        :param delivery_address_id: int value for Address id instance,
                                witch sets as delivery address
        :param billing_address_id: int value for Address id instance,
                                witch sets as billing address
        :param commit: Boolean value to do commit after save or not,
                                by default it is True
        """
        # TODO: Need to decide what kind of addresses is more impotant:

        assert kwargs['payment_method'] in current_app.config['PAYMENT_METHODS']
        delivery_address_id = kwargs.pop('delivery_address_id')
        billing_address_id = kwargs.pop('billing_address_id')
        kwargs.update(cls.__set_address(delivery_address_id, 'delivery'))
        kwargs.update(cls.__set_address(billing_address_id, 'billing'))

        goods = Cart.for_customer(kwargs['customer_id'])
        goods_price = sum(map(attrgetter('final_price'), goods))
        delivery_cost = cls.__resolve_delivery(kwargs['delivery_id'],
                                               delivery_address_id)

        kwargs.update({'goods': goods,
                       'goods_price': goods_price,
                       'total_cost': goods_price + delivery_cost})

        return super(Order, cls).create(**kwargs)
        # Some of fields can be calculated:
        # - get delivery and billing addresses from ids
        # - calculate vat
        # - get delivery_cost from Delivery.get_cost()
        # - goods_cost, total_cost

    @classmethod
    def __set_address(cls, address_id, addr_type):
        address_set = Address.query.get(address_id) \
                        .as_dict(exclude=['customer_id', 'created_at', 'id'])
        return dict(('{}_{}'.format(addr_type, key), value)
                    for key, value in address_set.iteritems())

    def resolve_payment(self):
        method = current_app.config['PAYMENT_METHODS'][self.payment_method]
        class_string = method['module']
        PaymentMethod = resolve_class(class_string)
        return PaymentMethod(self)

    @classmethod
    def __resolve_delivery(cls, delivery_id, address_id):
        delivery = Delivery.query.get(delivery_id)
        return delivery.calculate_price()

    def set_payment_details(self, payment_details):
        return self.update(payment_details=payment_details)

    @classmethod
    def get_by_payment_details(cls, payment_details):
        return cls.query.filter_by(payment_details)

    def mark_as_paid(self):
        return self.update(paid=True)


class Shelf(db.Model, CRUDMixin):
    """ Model to keep available products
    """
    price_option_id = db.Column(db.String(24), unique=True, index=True)
    quantity = db.Column(db.Integer, default=0)

    @classmethod
    def get_by_price_option(cls, price_option_id):
        """ Filter shelf items by price options
        """
        return cls.query.filter_by(price_option_id=price_option_id)


class Delivery(db.Model, CRUDMixin):
    name = db.Column(db.Unicode(255), unique=True, index=True)

    def calculate_price(self):
        """ method stub for delivery calculation
        """
        return 0

# TODO: add favorites
# TODO: what about related products?
# TODO: product.name need to translate?
# TODO: create trafaret for datetime
# TODO: m.b. need single model for producer
