from flamaster.core import db
from flamaster.core.models import CRUDMixin
from . import CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE


class Discount(db.Model, CRUDMixin):
    group_name = db.Column(db.String(255))
    discount = db.Column(db.Integer())
    group_type = db.Column(db.Enum(CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE))