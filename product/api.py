# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t
from flask import abort, request, session, json
from flask.ext.babel import lazy_gettext as _
from flask.ext.security import login_required, current_user

from flamaster.account.models import Customer

from flamaster.core import http, mongo
from flamaster.core.decorators import api_resource, method_wrapper
from flamaster.core.resources import ModelResource, MongoResource
from flamaster.core.utils import jsonify_status_code

from . import product as bp
from .helpers import resolve_parent
from .models import Cart, Category, Country, Order
from .datastore import OrderDatastore


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
        'image': t.MongoId
    }).append(resolve_parent).make_optional('parent_id', 'order', 'image') \
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
            datastore = OrderDatastore(self.model, Cart, Customer)
            instance = datastore.create_from_api(**self._request_data)
            response = self.serialize(instance)
        except t.DataError as err:
            status, response = http.BAD_REQUEST, err.as_dict()

        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if current_user.is_anonymous():
            kwargs['customer_id'] = session['customer_id']
        elif not current_user.is_superuser():
            kwargs['customer_id'] = current_user.customer.id
        # TODO: process product owners

        self.model is None and abort(http.BAD_REQUEST)
        return self.model.query.filter_by(**kwargs)

    @property
    def _request_data(self):
        try:
            data = request.json or json.loads(request.data)
            return self.clean(data)
        except t.DataError as err:
            raise err
        except:
            abort(http.BAD_REQUEST)
