from flamaster.core import db
from flamaster.core.models import CRUDMixin
from . import(CATEGORY_CHOICE,
              USER_CHOICE,
              PRODUCT_CHOICE,
              BASKET_CHOICE,
              PERCENT_CHOICE,
              CURRENCY_CHOICE)


class Discount(db.Model, CRUDMixin):
    """
    group_name - name op the discount group.
    discount_type - value of the discount in percents
    amount - value of the discount in percents or currency
    group_type - type of the discount group - choice field(category, product, user, basket)
    date_from - date, when discount became active
    date_to - discount finish date
    min_value - for basket type only, value of basket for free delivery
    shop_id - id of the store, which owns discount
    free_delivery - user dosen`t pay for the delivery, if this field is true
    """
    group_name = db.Column(db.String(255))
    discount_type = db.Column(db.Enum(PERCENT_CHOICE, CURRENCY_CHOICE))
    amount = db.Column(db.Numeric(precision=18, scale=2))
    group_type = db.Column(db.Enum(CATEGORY_CHOICE, USER_CHOICE, PRODUCT_CHOICE, BASKET_CHOICE))
    date_from = db.Column(db.Date)
    date_to = db.Column(db.Date)
    shop_id = db.Column(db.Integer())
    free_delivery = db.Column(db.Boolean, default=False)
    min_value = db.Column(db.Numeric(precision=18, scale=2))


class Discount_x_User(db.Model, CRUDMixin):
    """
    model m-m between discount and user, product, category
    """
    discount_id = db.Column(db.Integer())
    user_id = db.Column(db.Integer())

