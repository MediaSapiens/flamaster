from . import http, db

from flamaster.discount.models import Discount_x_Customer, Discount
from flamaster.discount import CART_CHOICE
from flamaster.account.models import Customer
from flamaster.core.utils import round_decimal

from datetime import date
from sqlalchemy import func, desc, or_, and_
from decimal import Decimal


class DiscountMixin(object):
    __goods_price = Decimal(0)
    customer_model = Customer

    def __calculate_discount(self, good, discount):
        """
        Calculation of discount, net_price, vat, gross_price for one good
        :param good: dict with goods params
        :param discount: value of discount
        :return:net_price, gross_price
        """

        net_price = good['net_price'] - discount
        vat = net_price*(good['vat'] / 100)
        gross_price = net_price + vat

        return (net_price, gross_price)

    def _get_prices_with_discount(self, item):
        prices = {}
        if item[0] == 'percent':
            for good in self.__goods:
                net_price, gross_price = self.__calculate_discount(good,
                                        good['net_price'] * (item[1] / 100))
                prices[good['id']] = {
                    'net': round_decimal(net_price),
                    'gross': round_decimal(gross_price),
                    'amount': good['amount']
                }
        else:
            discount = item[1] / sum([good['amount'] for good in self.__goods])
            for good in self.__goods:
                net_price, gross_price = self.__calculate_discount(good,
                                                                discount)
                prices[good['id']] = {
                    'net': round_decimal(net_price),
                    'gross': round_decimal(gross_price),
                    'amount': good['amount']
                }
        return prices

    def __get_discount(self, item, gross=False):
        total_net = 0
        total_gross = 0

        prices = self._get_prices_with_discount(item)
        total_net = sum(v['net'] * v['amount'] for v in prices.values())
        total_gross = sum(v['gross'] * v['amount'] for v in prices.values())

        if not gross:
            return Decimal(total_gross)

        return (Decimal(total_net), Decimal(total_gross), Decimal(total_discount))

    def _goods_as_dict(self, goods):
        goods_as_dict = []
        _calculate_vat = lambda good: good.product.get_vat().calculate(good.product.price)
        _calculate_new_vat = lambda good, price: good.product.get_vat().calculate(price)
        for good in goods:
            good_dict = good.as_dict()
            good_dict['net_price'] = Decimal(good.product.price) - _calculate_vat(good)
            goods_as_dict.append(good_dict)
        return goods_as_dict

    def _get_discounts(self, customer_id):
        now = date.today()
        items = db.session.query(Discount.discount_type, Discount.amount, Discount.free_delivery)\
            .filter(and_(self.customer_model.id == Discount_x_Customer.customer_id,
                         Discount_x_Customer.discount_id == Discount.id,
                         self.customer_model.id==customer_id,
                         Discount.date_from<=now,
                         Discount.date_to>=now)).all()
        if items is None:
            return None

        items.sort(key=self.__get_discount)
        return items


    def get_customer_discount(self, customer_id, goods, **kwargs):
        self.__goods = self._goods_as_dict(goods)

        goods_net = sum([good['net_price'] * good['amount'] for good in self.__goods])
        goods_gross = sum([good['unit_price'] * good['amount'] for good in self.__goods])
        items = self._get_discounts(customer_id)
        if items:
            max_discount = items[0]
            result = self.__get_discount(max_discount, gross=True)
        else:
            # If we don`t have discount for customer
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
