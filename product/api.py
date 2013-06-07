# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from flask import abort, request, session, json, current_app
from flask.ext.babel import lazy_gettext as _
from flask.ext.security import login_required, current_user

from flamaster.account.models import Customer

from flamaster.core import http, mongo
from flamaster.core.decorators import api_resource, method_wrapper
from flamaster.core.resources import ModelResource, MongoResource
from flamaster.core.utils import jsonify_status_code, round_decimal
from flamaster.product import OrderStates

from . import product as bp
from . import order_states_i18n
from .helpers import resolve_parent
from .models import Cart, Category, Country, Order, PaymentTransaction
from .datastore import OrderDatastore

import trafaret as t
from decimal import Decimal


__all__ = ['CategoryResource', 'CountriesResource', 'CartResource',
           'OrderResource']


@api_resource(bp, 'categories', {'id': int})
class CategoryResource(ModelResource):

    model = Category

    validation = t.Dict({
        'name': t.String,
        'description': t.String,
        'category_type': t.String,
        'parent_id': t.Int | t.Null,
        'order': t.Int,
        'image': t.String(allow_blank=True),
        'slug': t.String,
        'is_visible': t.Bool,
        'is_visible_in_nav': t.Bool
    }).append(resolve_parent).make_optional('parent_id', 'order', 'image',
                                            'is_visible', 'is_visible_in_nav') \
        .ignore_extra('*')

    filters_map = t.Dict({
        'parent_id': t.Int(gt=0)
    }).make_optional('parent_id').ignore_extra('*')

    def gen_list_response(self, **kwargs):
        return super(CategoryResource, self) \
            .gen_list_response(page_size=10000, **kwargs)


@api_resource(bp, 'countries', {'id': int})
class CountriesResource(ModelResource):
    model = Country

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def put(self, id, data):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def post(self, data):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def delete(self, id, data):
        return ''

    def gen_list_response(self, **kwargs):
        return super(CountriesResource, self) \
            .gen_list_response(page_size=10000, **kwargs)


@api_resource(bp, 'carts', {'id': int})
class CartResource(ModelResource):
    model = Cart
    optional_fields = ('service', 'product_variant_id',)
    validation = t.Dict({
        'product_id': t.MongoId,
        'product_variant_id': t.Null | t.MongoId,
        'amount': t.Int,
        'customer_id': t.Int,
        'service': t.String | t.Null
    }).make_optional(*optional_fields).ignore_extra('*')

    filters_map = t.Dict({
        'product_id': t.MongoId,
        'product_variant_id': t.MongoId
    }).make_optional('*').ignore_extra('*')

    def post(self):
        status = http.CREATED
        # Hack for IE XDomainRequest support:
        try:
            data = request.json or json.loads(request.data)
        except:
            abort(http.BAD_REQUEST)

        # condition to ensure that we have a customer when item added to cart
        if current_user.is_anonymous():
            customer_id = session.get('customer_id') or data.get('customer_id')
            if customer_id is not None:
                customer = Customer.query.get_or_404(customer_id)
            else:
                customer = Customer.create()
        else:
            customer = current_user.customer

        session['customer_id'] = customer.id
        data['customer_id'] = customer.id

        try:
            data = self.validation.check(data)
            product = mongo.db.products.find_one({'_id': data['product_id']})
            variant_id = data.get('product_variant_id', None)
            variant = mongo.db.product_variants.find_one({'_id': variant_id})

            if product is None:
                raise t.DataError({'product_id': _('Product not found')})

            if variant_id is not None and variant_id not in product.get('product_variants', []):
                raise t.DataError({'product_variant_id': _('Product variant not found')})

            cart = product.add_to_cart(customer=customer,
                                       amount=data['amount'],
                                       product_variant=variant,
                                       service=data.get('service'))

            response = cart.as_dict()
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def put(self, id):
        status = http.ACCEPTED
        data = request.json or abort(http.BAD_REQUEST)
        validation = self.validation.append(self._check_customer)

        try:
            data = validation.check(data)
            instance = self.get_object(id)

            if session['customer_id'] == instance.customer_id:
                response = instance.recalculate(data['amount']).as_dict()
            else:
                abort(http.UNAUTHORIZED)

        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if current_user.is_anonymous():
            kwargs['customer_id'] = session.get('customer_id', None)
        else:
            kwargs['customer_id'] = current_user.customer.id

        return super(CartResource, self).get_objects(**kwargs)

    def gen_list_response(self, **kwargs):
        return super(CartResource, self) \
            .gen_list_response(page_size=10000, **kwargs)

    def _check_customer(self, data):
        if data['customer_id'] != session['customer_id']:
            raise t.DataError({'customer_id': _('Unknown customer provided')})
        else:
            return data


# @api_resource(bp, 'products', {'id': None})
class ProductResource(MongoResource):
    """ Base resource for models based on BaseProduct
    """

    method_decorators = {
        'post': [login_required],
        'put': [login_required],
        'delete': [login_required]
    }


@api_resource(bp, 'orders', {'id': int})
class OrderResource(ModelResource):
    model = Order

    validation = t.Dict({
        'customer_id': t.Int,
        'next_state': t.Int,
        'payment_method': t.String,
        'payment_details': t.String,
        'delivery_provider_id': t.MongoId,
    }).make_optional('next_state', 'token',
                     'payment_details').ignore_extra('*')

    method_decorators = {
        'delete': [login_required]
    }

    filters_map = t.Dict({
        'state': t.Int
    }).make_optional('*').ignore_extra('*')

    def post(self):
        status = http.ACCEPTED

        try:
            datastore = OrderDatastore(self.model, Cart, Customer, PaymentTransaction)
            data = self._request_data

            if data['payment_method'] in current_app.config['REDIRECTED_PAYMENT_METHODS']:
                return datastore.create_from_request(**data)

            try:
                instance = datastore.create_from_api(**data)
                response = self.serialize(instance)
            except Exception:
                raise t.DataError({'payment_method': _('Unknown error')})

        except t.DataError as err:
            status, response = http.BAD_REQUEST, err.as_dict()

        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if current_user.is_anonymous():
            kwargs['customer_id'] = session['customer_id']
        else:
            kwargs['customer_id'] = current_user.customer.id
        # TODO: process product owners

        self.model is None and abort(http.BAD_REQUEST)
        return self.model.query.filter_by(**kwargs)\
            .filter(~(self.model.state == OrderStates.provider_denied))

    @property
    def _request_data(self):
        try:
            data = request.json or json.loads(request.data)
            return self.clean(data)
        except t.DataError as err:
            raise err
        except:
            abort(http.BAD_REQUEST)

    @classmethod
    def serialize(cls, instance, include=None):
        """ Method to controls model serialization in derived classes
        :rtype : dict
        """

        goods = instance.goods.all()
        if goods:
            vats = [c.product.get_vat().calculate(c.product.price) for c in goods]
            total_vat = round_decimal(Decimal(sum(vats)))
        else:
            total_vat = Decimal(0)

        data = instance.as_dict(api_fields=include)
        data.update({
            'state_name': order_states_i18n[str(instance.state)],
            'goods': [obj.as_dict() for obj in goods],
            'goods_count': len(goods),
            'total_vat': total_vat
        })

        if instance.billing_country_id:
            data['billing_country_name'] = instance.billing_country.name

        if instance.billing_country_id:
            data['delivery_country_name'] = instance.delivery_country.name

        return data
