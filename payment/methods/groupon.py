# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import trafaret as t
import requests
from flask import current_app, session
from flask.ext.babel import gettext as _
from requests.auth import HTTPBasicAuth

from flamaster.core import http
from flamaster.core.utils import jsonify_status_code
from flamaster.product.documents import BaseProductVariant
from flamaster.product.utils import get_order_class
from . import GROUPON
from .base import BasePaymentMethod


class GrouponPaymentMethod(BasePaymentMethod):
    method_name = GROUPON
    validation = t.Dict({
        'deal': t.Int,
        'voucher': t.String,
        'code': t.String,
        'variant': t.MongoId >> (lambda v: str(v))
    }).ignore_extra('*')

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

    def init_payment(self, payment_details=None):
        self.order.details = self.validation.check(payment_details)
        return self.process_payment()

    def process_payment(self):
        status = http.OK
        data = self.order.details
        data['status'] = 'OK'
        try:
            option_id = session.pop('valid_option', None)
            carts = self.order.goods.filter_by(price_option_id=option_id)
            if carts.count() != self.order.goods.count():
                raise t.DataError({'voucher': _('Invalid price option')})

            redemption = self.__redeem(voucher=data['voucher'],
                                       security=data['code'],
                                       deal=data['deal'])
            if redemption.status_code != http.OK:
                raise t.DataError({'voucher': _('Invalid voucher')})
            else:
                self.order.mark_paid()
                data.update(self.order.as_dict())
        except t.DataError as e:
            status = http.BAD_REQUEST
            data.update({
                'message': 'ERROR',
                'errors': e.as_dict(),
                'status': 'ERR'
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
            variant_id = data.pop('variant')
            order_cls = get_order_class()
            order = order_cls.get_by_payment_details(data)

            if order is not None:
                data.update({
                    'status': 'EXISTS',
                    'order': order.as_dict()
                })
                return jsonify_status_code(data, status)
            variant = BaseProductVariant.objects(id=variant_id).first()
            if variant is None:
                current_app.logger.debug("No variant")
                raise t.DataError({'deal': _('Invalid deal')})

            option, deal = self.__filter_option(variant, data['deal'])
            if option is None:
                current_app.logger.debug("No option")
                raise t.DataError({'deal': _('Invalid deal')})

            validation = self.__validate(voucher=data['voucher'],
                                         security=data['code'],
                                         deal=data['deal'])
            current_app.logger.info("Validation response: %s", validation)
            if validation.status_code != http.OK:
                raise t.DataError({'voucher': _('Invalid voucher')})

            session['valid_option'] = str(option.id)

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
