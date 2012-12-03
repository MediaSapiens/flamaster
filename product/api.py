# encoding: utf-8
import trafaret as t
from flask import abort, current_app, request, session, g
from flask.ext.babel import lazy_gettext as _
from flask.ext.security import login_required, current_user

from flamaster.account.models import Customer

from flamaster.core import http
from flamaster.core.decorators import api_resource
from flamaster.core.documents import MongoId
from flamaster.core.resources import ModelResource, MongoResource
from flamaster.core.utils import jsonify_status_code

from . import mongo, product as bp
from .models import Cart, Category, Country
from .helpers import resolve_parent

__all__ = ['CategoryResource']


@api_resource(bp, 'categories', {'id': int})
class CategoryResource(ModelResource):
    validation = t.Dict({
        'name': t.String,
        'description': t.String,
        'category_type': t.String,
        'parent_id': t.Int | t.Null,
    }).append(resolve_parent).make_optional('parent_id').ignore_extra('*')

    model = Category

    def paginate(self, page=1, page_size=1000, **kwargs):
        return super(CategoryResource, self).paginate(page, page_size,
                                                      **kwargs)

    def get_objects(self):
        query = super(CategoryResource, self).get_objects()
        if 'parent_id' in request.args:
            try:
                parent_id = int(request.args['parent_id'])
                query = query.filter_by(parent_id=parent_id)
            except ValueError as ex:
                current_app.logger.error("Exception: {0.message}".format(ex))
        return query


# @api_resource(bp, 'products', {'id': None})
class ProductResource(MongoResource):
    """ Base resource for models based on BaseProduct
    """

    method_decorators = {
        'post': [login_required],
        'put': [login_required],
        'delete': [login_required]
    }


@api_resource(bp, 'countries', {'id': int})
class CountriesResource(ModelResource):
    model = Country

    def put(self, id):
        abort(http.METHOD_NOT_ALLOWED)

    def post(self):
        abort(http.METHOD_NOT_ALLOWED)

    def delete(self, id=None):
        abort(http.METHOD_NOT_ALLOWED)

    def gen_list_response(self, page, **kwargs):
        return super(CountriesResource, self) \
            .gen_list_response(page, page_size=1000, **kwargs)


@api_resource(bp, 'carts', {'id': int})
class CartResource(ModelResource):
    model = Cart

    validation = t.Dict({
        'product_id': MongoId,
        'concrete_product_id': MongoId,
        'price_category_id': MongoId,
        'amount': t.Int,
        'customer_id': t.Int
    })

    def post(self):
        status = http.CREATED
        data = request.json or abort(http.BAD_REQUEST)
        validation = self.validation.make_optional('concrete_product_id')

        # condition to ensure that we have a customer when item added to cart
        if current_user.is_anonymous():
            customer = Customer.create()
            session['customer_id'] = customer.id
        else:
            session['customer_id'] = current_user.customer.id

        data['customer_id'] = session['customer_id']

        try:
            data = validation.check(data)
            product = mongo.db.products.find_one({'_id': data['product_id']})
            if product is None:
                raise t.DataError({'product_id': _('Product not fount')})

            cart = product.add_to_cart(customer=g.user, amount=data['amount'],
                                       price_option_id=data['price_option_id'])

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
                response = instance.update(amount=data['amount']).as_dict()
            else:
                abort(http.UNAUTHORIZED)
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def get_objects(self):
        return self.model.query.filter_by(is_ordered=False)

    def _check_customer(self, data):
        if data['customer_id'] != session['customer_id']:
            raise t.DataError({'customer_id': _('Unknown customer provided')})
        else:
            return data
