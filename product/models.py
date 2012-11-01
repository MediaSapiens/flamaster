# -*- encoding: utf-8 -*-
import trafaret as t

from datetime import datetime
from bson import DBRef, ObjectId
from flask import current_app
from operator import attrgetter
from sqlalchemy.ext.hybrid import hybrid_property

from flamaster.core import COUNTRY_CHOICES, lazy_cascade
from flamaster.core.documents import Document
from flamaster.core.models import CRUDMixin, TreeNode, NodeMetaClass
from flamaster.core.utils import resolve_class

from . import db, mongo


__all__ = ['Category', 'Customer', 'Favorite', 'BaseProduct', 'Shelf',
           'Address']


class Address(db.Model, CRUDMixin):
    """ Represents address data for users
        By default model inherits id and created_at fields from the CRUDMixin
    """
    __mapper_args__ = {
        'order_by': ['city', 'street']
    }
    city = db.Column(db.Unicode(255), nullable=False)
    street = db.Column(db.Unicode(255), nullable=False)
    apartment = db.Column(db.Unicode(20), nullable=False)
    zip_code = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id',
                                                      ondelete='CASCADE',
                                                      use_alter=True,
                                                      name='fk_customer_id'))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    country = db.relationship('Country')

    def __init__(self, **kwargs):
        assert 'city' in kwargs and 'street' in kwargs
        self.type = kwargs.pop('type', 'delivery')
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return "<Address:('%s','%s')>" % (self.city, self.street)

    def save(self, commit=True):
        if self.type == 'billing':
            Address.query.filter_by(user=self.user).\
                          update({'type': 'delivery'})
        return super(Address, self).save(commit)


class BaseProduct(Document):
    __abstract__ = True
    __collection__ = 'products'
    structure = t.Dict({
        'sku': t.String,
        'name': t.String,
        'type': t.String,
        'teaser': t.String,
        'description': t.String,
        # 'producer': t.Int,
        'categories': t.List[t.Int],
        'updated_at': t.Any,
        'created_by': t.Int,
        'accessories': t.List[t.Type(Document) | t.Type(DBRef)],
        t.Key('created_at', default=datetime.utcnow): t.Any
    })
    required_fields = ['name', 'type', 'categories', 'created_by']
    i18n = ['name', 'teaser', 'description']
    indexes = ['id', 'categories', ('updated_at', -1), ('created_at', -1),
               'created_by', 'type']

    def get_price(self, *args, **kwargs):
    # WARNING!
    # We have another architectural problem here.
    # We get ID PriceCategory to price calculation.
    # But PriceCategory class is in the module event,
    # which should be completely encapsulated from the module product.
        raise NotImplemented('Method is not implemented')

    def add_to_shelf(self, prices):
        for price in prices:
            Shelf.create(price_category_id=str(price.id),
                         quantity=price.quantity)

    def get_from_shelf(self, **kwargs):
        return Shelf.query.with_lockmode('update_nowait').filter_by(**kwargs)

    def add_to_cart(self, *args, **kwargs):
        kwargs['product'] = self
        return Cart.create(*args, **kwargs)


class Cart(db.Model, CRUDMixin):
    """ Cart record for concrete product
    """
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.String, nullable=False)
    concrete_product_id = db.Column(db.String, nullable=False)
    price_category_id = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(precision=18, scale=2))
    final_price = db.Column(db.Numeric(precision=18, scale=2))
    is_ordered = db.Column(db.Boolean, default=False, index=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    customer = db.relationship('Customer',
                               backref=db.backref('carts', **lazy_cascade))

    @classmethod
    def create(cls, **kwargs):
        """ Cart creation method. Accepted params are:
        :param product: BaseProduct or it's subclass instance
        :param concrete_product_id: bson.ObjectId key for concrete product
                                    value
        :param price_categoey_id: bson.ObjectId key for price category
                                  identifier
        :param amount: amount of products to place in cart
        :param customer_id: int value for customer id instance
        """
        product = kwargs.pop('product')
        price, final_price = product.get_price(kwargs['price_category_id'],
                                        kwargs['amount'])

        kwargs.update({
            'product_id': str(product.id),
            'concrete_product_id': str(kwargs['concrete_product_id']),
            'price_category_id': str(kwargs['price_category_id']),
            'price': price,
            'final_price': final_price,
        })
        return super(Cart, cls).create(commit=False, **kwargs)

    @property
    def product(self):
        return BaseProduct.query.find_one({'_id': ObjectId(self.product_id)})

    @classmethod
    def for_customer(cls, customer_id):
        """ helper method for obtaining cart records for concrete customer
        """
        return cls.filter_by(customer_id=customer_id, is_ordered=False)


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
    api_fields = ['id', 'short', 'long']

    short = db.Column(db.Unicode(3), nullable=False, index=True)

    @property
    def long(self):
        return COUNTRY_CHOICES[self.short]


class Customer(db.Model, CRUDMixin):

    first_name = db.Column(db.Unicode(255), default=u'')
    last_name = db.Column(db.Unicode(255), default=u'')
    email = db.Column(db.String(80), index=True)
    phone = db.Column(db.String(80), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.UnicodeText)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", backref=db.backref("customer",
                                                      uselist=False))
    addresses = db.relationship('Address', backref=db.backref('customer'),
                        primaryjoin="Address.customer_id==Customer.id",
                        cascade='all, delete', lazy='dynamic')
    billing_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id',
                        use_alter=True, name='fk_billing_address'))
    _billing_address = db.relationship("Address", cascade='all, delete',
                        primaryjoin="Customer.billing_address_id==Address.id",
                        backref=db.backref("billing_for_customer",
                                           uselist=False))
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id',
                        use_alter=True, name='fk_delivery_address'))
    _delivery_address = db.relationship("Address", cascade='all, delete',
                        primaryjoin="Customer.delivery_address_id==Address.id",
                        backref=db.backref("delivery_for_customer",
                                           uselist=False))

    def __unicode__(self):
        return "{0.first_name} {0.last_name}".format(self)

    @property
    def addresses_ids(self):
        return map(attrgetter('id'), self.addresses)

    def set_address(self, addr_type, value):
        if not isinstance(value, (int, Address)):
            raise ValueError('value is neither int nor Address instance')

        if isinstance(value, int):
            value = Address.query.get(value)

        if value.id not in self.addresses_ids:
            self.addresses.append(value)

        setattr(self, "{}_address_id".format(addr_type), value.id)

    @hybrid_property
    def billing_address(self):
        """ Hybrid property allowing only one billing-address per-customer
        """
        return self._billing_address

    @billing_address.setter
    def billing_address(self, value):
        """ setter for billing_address property
        """
        self.set_address('billing', value)

    @hybrid_property
    def delivery_address(self):
        """ Hybrid property allowing only one delivery_address per-customer
        """
        return self._delivery_address

    @delivery_address.setter
    def delivery_address(self, value):
        """ setter for delivery_address property
        """
        self.set_address('delivery', value)


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

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
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
        assert kwargs['payment_method'] in current_app.config['PAYMENT_MEHODS']
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
        method = current_app.config['PAYMENT_MEHODS'][self.payment_method]
        class_string = method['module']
        PaymentMethod = resolve_class(class_string)
        return PaymentMethod()

    @classmethod
    def __resolve_delivery(cls, delivery_id, address_id):
        delivery = Delivery.query.get(delivery_id)
        return delivery.calculate_price()


@mongo.register
class ProductType(Document):

    structure = t.Dict({
        'name': t.String,
        'attrs': t.Mapping(t.String, t.String),
        t.Key('created_at', default=datetime.utcnow): t.Any
    })

    i18n = ['attrs']
    indexes = ['name']


class Shelf(db.Model, CRUDMixin):
    """ Model to keep available products
    """
    price_category_id = db.Column(db.String(24), unique=True, index=True)
    quantity = db.Column(db.Integer, default=0)


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
