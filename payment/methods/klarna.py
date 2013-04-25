from __future__ import absolute_import

from flask import request

from klarna import Klarna, Config, Address
from klarna.const import GoodsIs, GenderMap

from .base import BasePaymentMethod


class KlarnaPaymentMethod(BasePaymentMethod):
    method_name = 'klarna'

    def __init__(self, *args, **kwargs):
        super(KlarnaPaymentMethod, self).__init__(*args, **kwargs)

        self.klarna = Klarna(Config(**self.settings))
        self.klarna.init()

    def init_payment(self):
        self.klarna.clientip = '83.10.0.5'#request.remote_addr
        self.klarna.shipping = self.__get_address('delivery')
        self.klarna.billing = self.__get_address('billing')

        self.klarna.set_estore_info(orderid1=self.order.reference)

        goods = self.order.goods.all()

        for art in goods:
            self.klarna.add_article(qty=art.amount,
                                    title=art.product.name,
                                    price=float(art.price),
                                    vat=19,
                                    discount=0,
                                    flags=GoodsIs.INC_VAT)

        if self.order.delivery_price is not None:
            self.klarna.add_article(qty=1,
                                    title='Shipment Fee',
                                    price=float(self.order.delivery_price),
                                    vat=0,
                                    flags=GoodsIs.SHIPPING)

        if self.order.payment_fee is not None:
            self.klarna.add_article(qty=1,
                                    title='Payment Fee',
                                    price=float(self.order.payment_fee),
                                    vat=0,
                                    flags=GoodsIs.NOFLAG)

    def __get_address(self, addr_type):
        _get = lambda k: getattr(self.order, '{0}_{1}'.format(addr_type, k))
        return Address(email=self.order.customer.email,
                       telno=_get('phone').replace(' ', '').replace('+', ''),
                       fname=_get('first_name'),
                       lname=_get('last_name'),
                       street=_get('street'),
                       zip=_get('zip_code'),
                       city=_get('city'),
                       country=_get('country').short,
                       house_number=_get('apartment'),
                       house_extension=None)


    def process_payment(self):
        self.init_payment()
        customer = self.order.customer
        pno = '{:%d%m%Y}'.format(customer.birth_date)
        return self.klarna.add_transaction(gender=GenderMap[customer.gender],
                                           pno=pno,
                                           flags=0)
