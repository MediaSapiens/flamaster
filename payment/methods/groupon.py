# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t
import requests

from flask import current_app, json

from flamaster.core import http
from flamaster.core.utils import jsonify_status_code
from flamaster.product.documents import BaseProductVariant
from flamaster.product.models import Order

from requests.auth import HTTPBasicAuth

from .base import BasePaymentMethod


class GrouponPaymentMethod(BasePaymentMethod):
    method_name = 'groupon'
    validation = t.Dict({
        'deal': t.Int,
        'voucher': t.String,
        'code': t.String,
        'variant': t.Or(t.MongoId, t.Null)
    }).make_optional('variant')

    validate_path = 'merchant/redemptions/validate'
    redeem_path = 'merchant/redemptions'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/xml'
    }
    data_template = """<redemption xmlns="http://www.api.citydeal.com/v1"
                    deal_id="{deal}" part1_provider_only="{security}"
                    part2_provider_customer="{voucher}" />"""

    def __do_request(self, endpoint, **kwargs):
        login, passwd = self.settings['name'], self.settings['password']
        data = self.data_template.format(**kwargs).encode('utf-8')
        if self.sandbox:
            return current_app.make_response('')
        else:
            return requests.post(endpoint, data=data,
                                 auth=HTTPBasicAuth(login, passwd),
                                 headers=self.headers)

    def __validate(self, **kwargs):
        endpoint_tpl = self.settings['endpoint']
        endpoint = endpoint_tpl.format(path=self.validate_path)
        return self.__do_request(endpoint, **kwargs)

    def __redeem(self, **kwargs):
        endpoint_tpl = self.settings['endpoint']
        endpoint = endpoint_tpl.format(path=self.redeem_path)
        return self.__do_request(endpoint, **kwargs)

    def process_payment(self):
        status = http.OK
        try:
            data = json.loads(self.order.payment_details)
            redemption = self.__redeem(voucher=data['voucher'],
                                       security=data['code'],
                                       deal=data['deal'])
            if redemption.status_code != http.OK:
                raise t.DataError({'voucher': u'InvalidVoucher'})

        except t.DataError as e:
            status = http.BAD_REQUEST
            data.update({
                'message': 'ERROR',
                'exception': e.as_dict(),
            })

        return jsonify_status_code(data, status)

    def __filter_option(self, variant, cda):
        for option in variant.price_options:
            for deal in option.groupon:
                if deal.cda == cda:
                    return option, deal
        return None, None

    def verify(self, data):
        status = http.OK
        try:
            data = self.validation.check(data)

            order = Order.get_by_payment_details(data, fuzzy=True)
            if order is not None:
                data.update({'status': 'EXISTS'})
                return jsonify_status_code(data, status)

            variant = BaseProductVariant.objects(
                            price_options__groupon__cda=data['deal']).first()
            if variant is None:
                raise t.DataError({'deal': u'Invalid deal'})

            option, deal = self.__filter_option(variant, data['deal'])
            if option is None:
                raise t.DataError({'deal': u'Invalid deal'})

            validation = self.__validate(voucher=data['voucher'],
                                         security=data['code'],
                                         deal=data['deal'])
            if validation.status_code != http.OK:
                raise t.DataError({'voucher': u'InvalidVoucher'})
            data.update({
                'status': 'OK',
                'seats': deal['number'],
                'option': option,
            })
        except t.DataError as e:
            data.update({
                'status': 'ERR',
                'errors': e.as_dict()
            })

        return jsonify_status_code(data, status)
