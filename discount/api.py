from flask.ext.security import roles_required

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource

from flamaster.discount.models import Discount, Discount_x_User

from wimoto.utils.api import admin_role

import trafaret as t

from . import (CATEGORY_CHOICE,
               USER_CHOICE,
               PRODUCT_CHOICE,
               BASKET_CHOICE,
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
        "group_type": t.Enum(CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE, BASKET_CHOICE),
        "date_from": t.DateTime,
        "date_to": t.DateTime,
        "shop_id": t.Int,
        t.Key('free_delivery', default=False): t.Bool,
        "min_value": t.Float
        }).ignore_extra('*')


@api_resource(discount, 'user', {'id': None})
class DiscountUserResource(ModelResource):
    model = Discount_x_User

    method_decorators = {
        'post': [roles_required(admin_role)],
        'put': [roles_required(admin_role)],
        'delete': [roles_required(admin_role)]
    }

    validation = t.Dict({
        "discount_id": t.Int,
        "user_id":t.Int})

    def get_objects(self, **kwargs):
        if 'discount_id' in request.args:
            kwargs['discount_id'] = request.args['discount_id']
        if 'user_id' in request.args:
            kwargs['user_id'] = request.args['user_id']
        return self.model.query.filter_by(**kwargs)

