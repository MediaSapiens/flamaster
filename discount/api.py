from datetime import datetime

from flask.ext.security import roles_required
from flask import current_app
from flask.ext.babel import lazy_gettext as _

from sqlalchemy import or_

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource
from flamaster.core.utils import jsonify_status_code
from flamaster.account.models import Customer
# from flamaster.account.api import CustomerResource
from flamaster.discount.models import Discount, Discount_x_Customer

from wimoto.utils.api import admin_role
from werkzeug.exceptions import BadRequest

import trafaret as t

from . import (CATEGORY_CHOICE,
               USER_CHOICE,
               PRODUCT_CHOICE,
               CART_CHOICE,
               PERCENT_CHOICE,
               CURRENCY_CHOICE,
               discount)

from flask import request
@api_resource(discount, 'groups', {'id': None})
class DiscountResource(ModelResource):
    model = Discount

    method_decorators = {
        'post': [roles_required(admin_role)],
        'put': [roles_required(admin_role)],
        'delete': [roles_required(admin_role)]
    }

    validation = t.Dict({
        "group_name": t.String,
        "discount_type": t.Enum(CURRENCY_CHOICE, PERCENT_CHOICE),
        "amount":t.Float,
        "group_type": t.Enum(CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE, CART_CHOICE),
        "date_from": t.DateTime,
        "date_to": t.DateTime,
        "shop_id": t.Int,
        t.Key('free_delivery', default=False): t.Bool,
        "min_value": t.Float
        }).ignore_extra('*').make_optional("date_from", "date_to", "min_value")

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        query = self.model.query.filter_by(**kwargs)

        if 'q' in request.args and request.args['q']:

            q = request.args['q']
            q = "%"+q+"%"
            search_filters = Discount.group_name.like(q)

            query = query.filter(search_filters)

        if 'o' in request.args:

            order_map = {'group_name': Discount.group_name,
                         'group_type': Discount.group_type,
                         'amount': Discount.amount,
                         'discount_type':Discount.discount_type}

            try:
                order_field = order_map[request.args['o']]
            except KeyError, e:
                raise BadRequest(u"Unsupported attribute value: o=%s" % e)

            ot = request.args.get('ot', 'asc')
            if ot == 'desc':
                order_field = order_field.desc()

            query = query.order_by(order_field)

        return query

    def clean(self, data):
        if 'date_from' in data:
            date = data['date_from'].split('-')
            count_date = len([x for x in date if x!=''])
            if (count_date != 0 and count_date != 3):
                raise t.DataError({'date_from': _('incorrect format')})
            if (count_date == 0):
                data.pop('date_from')

        if 'date_to' in data:
            date = data['date_to'].split('-')
            count_date = len([x for x in date if x!=''])
            if (count_date != 0 and count_date != 3):
                raise t.DataError({'date_to': _('incorrect format')})
            if (count_date == 0):
                data.pop('date_to')

        # TODO: change comparison
        if ('date_from' in data) and ('date_to' in data):
            if (datetime.strptime(data["date_from"], "%Y-%m-%d") >
                    datetime.strptime(data["date_to"], "%Y-%m-%d")):
                raise t.DataError({'date_to': _('range is incorrect')})
        data = super(DiscountResource, self).clean(data)

        return data


@api_resource(discount, 'customer', {'id': None})
class DiscountCustomerResource(ModelResource):
    model = Discount_x_Customer

    method_decorators = {
        'post': [roles_required(admin_role)],
        'put': [roles_required(admin_role)],
        'delete': [roles_required(admin_role)]
    }

    validation = t.Dict({
        "discount_id": t.Int,
        "customer_id":t.Int})

    def get(self, id=None):
        if id is None:
            response = self.gen_list_response()
            response = self.make_response(response)
        else:
            response = self.serialize(self.get_object(id))
            if response:
                response.update(self.get_params(response['customer_id']))
        return jsonify_status_code(response)

    def make_response(self, response):
        for object in response["objects"]:
            object.update(self.get_params(object['customer_id']))
        return response

    def get_params(self, customer_id):
        result = dict()
        customer = Customer.query.filter_by(id=customer_id).first().as_dict()
        if customer:
            result['first_name'] = customer['first_name']
            result['last_name'] = customer['last_name']
            result['email'] = customer['email']
        return result

    def get_objects(self, **kwargs):
        if 'discount_id' in request.args:
            kwargs['discount_id'] = request.args['discount_id']
        if 'customer_id' in request.args:
            kwargs['customer_id'] = request.args['customer_id']

        query = self.model.query.filter_by(**kwargs)

        query = query.join(Customer)

        if 'q' in request.args and request.args['q']:
            q = request.args['q']
            q = "%"+q+"%"
            search_filters = (Customer.email.like(q),
                              Customer.first_name.like(q),
                              Customer.last_name.like(q))

            query = query.filter(or_(*search_filters))

        if 'o' in request.args:

            order_map = {'first_name': Customer.first_name,
                         'last_name': Customer.last_name,
                         'email': Customer.email}

            try:
                order_field = order_map[request.args['o']]
            except KeyError, e:
                raise BadRequest(u"Unsupported attribute value: o=%s" % e)

            ot = request.args.get('ot', 'asc')
            if ot == 'desc':
                order_field = order_field.desc()

            query = query.order_by(order_field)

        return query


