# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app

from flamaster.core import COUNTRY_CHOICES, lazy_cascade, db
from flamaster.core.decorators import multilingual
from flamaster.core.models import CRUDMixin, TreeNode, NodeMetaClass
from flamaster.core import mongo

from werkzeug.utils import import_string
from bson import ObjectId

from . import OrderStates


__all__ = ['Cart', 'Category', 'Favorite', 'Order', 'Shelf']


class Cart(db.Model, CRUDMixin):
    """ Cart record for concrete product
    """
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.String, nullable=False)
    product_variant_id = db.Column(db.String)
    service = db.Column(db.String)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(precision=18, scale=2))
    is_ordered = db.Column(db.Boolean, default=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    customer = db.relationship('Customer',
                               backref=db.backref('carts', **lazy_cascade))

    @classmethod
    def create(cls, amount, customer, product, product_variant=None, service=''):
        """ Cart creation method. Accepted params are:
        :param product: BaseProduct or it's subclass instance
        :param product_variant: instance of BaseProductVariant subclass
        :param amount: amount of products to place in cart
        :param customer_id: instance of Customer model
        """
        instance_kwargs = {
            'product_id': str(product.id),
            'price': product.get_price(product_variant, amount),
            'customer': customer,
            'amount': amount,
            'service': service
        }

        if product_variant is not None:
            instance_kwargs['product_variant_id'] = str(product_variant.id)

        return super(Cart, cls).create(**instance_kwargs)

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

    @property
    def product(self):
        return mongo.db.products.find_one({'_id': ObjectId(self.product_id)})

    @property
    def product_variant(self):
        return mongo.db.product_variants.find_one({
            '_id': ObjectId(self.product_variant_id)})

    def recalculate(self, amount):
        new_price = self.product.get_price(self.product_variant, amount)
        return self.update(amount=amount, price=new_price)


@multilingual
class Category(db.Model, TreeNode):
    """ Product category mixin
    """
    __metaclass__ = NodeMetaClass
    __mp_manager__ = 'mp'

    name = db.Column(db.Unicode(256))
    description = db.Column(db.UnicodeText)
    category_type = db.Column(db.String, nullable=False, default='catalog')
    order = db.Column(db.Integer, default=0)
    image = db.Column(db.String(256), default='')
    is_deleted = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)

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
    shop_id = db.Column(db.String(128), default=current_app.config['SHOP_ID'])
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

    vat = db.Column(db.Numeric(precision=18, scale=2))
    total_price = db.Column(db.Numeric(precision=18, scale=2))

    payment_details = db.Column(db.UnicodeText, unique=True)
    payment_method = db.Column(db.String, nullable=False, index=True)
    state = db.Column(db.Integer, index=True)
    # stored cost for the order delivery
    delivery_method = db.Column(db.String, nullable=False, index=True)
    delivery_price = db.Column(db.Numeric(precision=18, scale=2))

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False, index=True)
    customer = db.relationship('Customer',
                               backref=db.backref('orders', **lazy_cascade))

    goods = db.relationship('Cart', backref='order', **lazy_cascade)
    notes = db.Column(db.UnicodeText, default=u'')

    def resolve_payment(self, method=None):
        payment_method = self.payment_method or method
        method = current_app.config['PAYMENT_METHODS'][payment_method]
        class_string = method['module']
        PaymentMethod = import_string(class_string)
        return PaymentMethod(self)

    @classmethod
    def __resolve_delivery(cls, delivery, address):
        return delivery.calculate_price()

    def set_payment_details(self, payment_details):
        return self.update(payment_details=payment_details)

    @classmethod
    def get_by_payment_details(cls, payment_details):
        return cls.query.filter_by(payment_details=payment_details).first()

    def mark_paid(self):
        return self.update(state=OrderStates.paid)


class Shelf(db.Model, CRUDMixin):
    """ Model to keep available products
    """
    product_id = db.Column(db.String, nullable=False, unique=True, index=True)
    product_variant_id = db.Column(db.String(24))
    quantity = db.Column(db.Integer, default=0)

    @classmethod
    def get_by_product_variant(cls, product_variant_id):
        """ Filter shelf items by price options
        """
        if not isinstance(product_variant_id, basestring):
            product_variant_id = str(product_variant_id)
        return cls.query.filter_by(product_variant_id=product_variant_id)


# TODO: add favorites
# TODO: what about related products?
# TODO: product.name need to translate?
# TODO: create trafaret for datetime
# TODO: m.b. need single model for producer
