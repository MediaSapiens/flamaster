from flask.ext.security import roles_required

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource

from flamaster.discount.models import Discount, Discount_x_Object

from wimoto.utils.api import admin_role

import trafaret as t

from . import CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE, BASKET_CHOICE, discount


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
        "discount": t.Int,
        "group_type": t.Enum(CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE, BASKET_CHOICE),
        "date_from": t.DateTime,
        "date_to": t.DateTime,
        t.Key('free_delivery', default=False): t.Bool,
        "min_value": t.Float
        }).ignore_extra('*')


@api_resource(discount, 'objects', {'id': None})
class DiscountObjectResource(ModelResource):
    model = Discount_x_Object

    method_decorators = {
        'post': [roles_required(admin_role)],
        'put': [roles_required(admin_role)],
        'delete': [roles_required(admin_role)]
    }

    validation = t.Dict({
        "discount_id": t.Int,
        "object_id":t.Int})
