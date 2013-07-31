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

    def __calculate_discount(self, good, discount):
        net_price = good['net_price'] - discount
        gross_price = net_price + (net_price * (good['vat'] / 100))
        return (net_price, gross_price)

    def __get_discount(self, item, gross=False):
        total_net = 0
        total_gross = 0

        if item[0] == 'percent':
            for good in self.__goods:
                net_price, gross_price = self.__calculate_discount(good,
                                        good['net_price'] * (item[1] / 100))
                total_net += net_price * good['amount']
                total_gross += gross_price * good['amount']
        else:
            discount = item[1] / sum([good['amount'] for good in self.__goods])
            for good in self.__goods:
                net_price, gross_price = self.__calculate_discount(good, discount)
                total_net += net_price * good['amount']
                total_gross += gross_price * good['amount']

        if not gross:
            return Decimal(total_gross)

        return (Decimal(total_net), Decimal(total_gross))

    def __goods_as_dict(self, goods):
        goods_as_dict = []
        _calculate_vat = lambda good: good.product.get_vat().calculate(good.product.price)
        for good in goods:
            good_dict = good.as_dict()
            good_dict['net_price'] = Decimal(good.product.price) - _calculate_vat(good)
            goods_as_dict.append(good_dict)
        return goods_as_dict

    def get_customer_discount(self, customer_id, goods, **kwargs):
        self.__goods = self.__goods_as_dict(goods)

        goods_net = sum([good['net_price'] * good['amount'] for good in self.__goods])
        goods_gross = sum([good['unit_price'] * good['amount'] for good in self.__goods])
        now = date.today()
        items = db.session.query(Discount.discount_type, Discount.amount, Discount.free_delivery)\
            .filter(and_(self.customer_model.id == Discount_x_Customer.customer_id,
                         Discount_x_Customer.discount_id == Discount.id,
                         self.customer_model.id==customer_id,
                         Discount.date_from<=now,
                         Discount.date_to>=now)).all()

        if items:
            items.sort(key=self.__get_discount)
            max_discount = items[0]
            result = self.__get_discount(max_discount, gross=True)
            result += (goods_net - result[0],)
        else:
            result = (
                Decimal(goods_net),
                Decimal(goods_gross),
                Decimal(0)
            )

        return result

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
