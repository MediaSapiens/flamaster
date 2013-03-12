# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t
from flask import request, session
from flask.ext.babel import lazy_gettext as _
from flask.ext.security import login_required, current_user

from flamaster.account.models import Customer
from flamaster.account.api import CustomerMixin
from flamaster.core import http
from flamaster.core.decorators import method_wrapper
from flamaster.core.resources import ModelResource
from flamaster.core.utils import jsonify_status_code

from .helpers import resolve_parent
from .documents import BaseProduct
from .models import Category, Country
from .utils import get_order_class, get_cart_class


__all__ = ['CategoryResource', 'CountryResource', 'CartResource',
           'OrderResource']


class CategoryResource(ModelResource):
    page_size = 10000
    model = Category

    validation = t.Dict({
        'name': t.String,
        'description': t.String,
        'category_type': t.String,
        'parent_id': t.Int | t.Null,
        'order': t.Int,
    }).append(resolve_parent).make_optional('parent_id', 'order') \
        .ignore_extra('*')

    filters_map = t.Dict({
        'parent_id': t.Int(gt=0)
    }).make_optional('parent_id').ignore_extra('*')


class CountryResource(ModelResource):
    model = Country
    page_size = 1000

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def put(self, id, data):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def post(self, data):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def delete(self, id, data):
        return ''

    @classmethod
    def serialize(cls, instance):
        """ Method to controls model serialization in derived classes
        :rtype : dict
        """
        return instance.as_dict(include=['id', 'short', 'name'])


class CartResource(ModelResource, CustomerMixin):
    model = get_cart_class()
    page_size = 10000

    validation = t.Dict({
        'product_id': t.MongoId,
        'concrete_product_id': t.MongoId,
        'price_option_id': t.MongoId,
        'amount': t.Int,
        'service': t.String
    }).make_optional('service', 'concrete_product_id').ignore_extra('*')

    filters_map = t.Dict({
        'product_id': t.MongoId,
        'product_variant_id': t.MongoId
    }).make_optional('*').ignore_extra('*')

    def post(self):
        status = http.CREATED
        customer = self._customer
        session['customer_id'] = customer.id

        try:
            data = self.clean(request.json)
            # TODO: resolve add to cart method
            product = BaseProduct.objects(pk=data['product_id']).first()
            if product is None:
                raise t.DataError({'product_id': _('Product not fount')})

            cart = product.add_to_cart(customer=customer,
                                       amount=data['amount'],
                                       price_option_id=data['price_option_id'])
            # cart.details = service_data

            response = self.serialize(cart)
        except t.DataError as err:
            status, response = http.BAD_REQUEST, err.as_dict()

        return jsonify_status_code(response, status)

    def put(self, id):
        status = http.ACCEPTED

        try:
            data = self.clean(request.json)
            instance = self.get_object(id).update(amount=data['amount'])
            response = self.serialize(instance)
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if not current_user.is_superuser():
            kwargs['customer_id'] = session.get('customer_id')

        return super(CartResource, self).get_objects(**kwargs)

    @property
    def _customer(self):
        if current_user.is_anonymous():
            customer_id = session.get('customer_id')
            if customer_id is None:
                customer = Customer.create()
            else:
                customer = Customer.query.get_or_404(customer_id)
        else:
            customer = current_user.customer

        return customer


class OrderResource(ModelResource, CustomerMixin):
    model = get_order_class()

    validation = t.Dict({
        'next_state': t.Int,
        'payment_method': t.String,
        'payment_details': t.String
    }).make_optional('next_state',
                     'payment_method',
                     'payment_details').ignore_extra('*')

    method_decorators = {
        'delete': [login_required]
    }

    def post(self):
        status = http.ACCEPTED

        try:
            instance = self.model.create_from_api(**request.json)
            response = self.serialize(instance)
        except t.DataError as err:
            status, response = http.BAD_REQUEST, err.as_dict()

        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if not current_user.is_superuser():
            kwargs['customer_id'] = self._customer.id

        return super(OrderResource, self).get_objects(**kwargs)
