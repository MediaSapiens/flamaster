# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from flamaster.core import lazy_cascade
from flamaster.extensions import db
from flamaster.conf.settings import SHOP_ID

from flask import current_app
from werkzeug.utils import import_string

from . import OrderStates


class OrderMixin(object):

    shop_id = db.Column(db.String(128), default=SHOP_ID)
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
