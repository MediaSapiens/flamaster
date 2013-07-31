from . import http, db

from flamaster.discount.models import Discount_x_Customer, Discount
from flamaster.discount import CART_CHOICE
from flamaster.account.models import Customer

from datetime import date
from sqlalchemy import func, desc, or_, and_
from decimal import Decimal


class DiscountMixin(object):
    __goods_price = Decimal(0)
    customer_model = Customer

    def __get_discount(self, item):
        if item[0] == 'percent':
            return self.__goods_price * (item[1] / 100)
        else:
            return item[1]

    def get_customer_discount(self, customer_id, goods_price, **kwargs):
        self.__goods_price = goods_price
        now = date.today()
        items = db.session.query(Discount.discount_type, Discount.amount, Discount.free_delivery)\
            .filter(and_(self.customer_model.id == Discount_x_Customer.customer_id,
                         Discount_x_Customer.discount_id == Discount.id,
                         self.customer_model.id==customer_id,
                         Discount.date_from<=now,
                         Discount.date_to>=now)).all()

        if items:
            items.sort(key=self.__get_discount)
            max_discount = items[-1]
            return self.__get_discount(max_discount)

        return Decimal(0)

    def get_cart_discount(self, goods_price):
        now = date.today()
        items = db.session.query(Discount.discount_type, Discount.amount,
                                 Discount.free_delivery, Discount.min_value) \
            .filter(and_(Discount.date_from<=now,
                         Discount.date_to>=now,
                         Discount.group_type==CART_CHOICE,
                         Discount.min_value<=goods_price,
                         )).all()
        if items:
            return True
        return False
