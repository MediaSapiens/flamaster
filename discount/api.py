from flask.ext.security import roles_required

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource

from flamaster.discount.models import Discount

from wimoto.utils.api import admin_role

import trafaret as t

from . import CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE, discount


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
        "group_type":t.Enum(CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE)
        }).ignore_extra('*')