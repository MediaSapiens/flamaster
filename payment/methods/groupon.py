# -*- encoding: utf-8 -*-
from bson import ObjectId
from flamaster.core import http
from flamaster.core.utils import jsonify_status_code
from .base import BasePaymentMethod
from .. import mongo


class GrouponPaymentMethod(BasePaymentMethod):
    method_name = 'groupon'

    def init_payment(self):  # amount, currency, description):
        raise NotImplementedError

    def precess_payment_response(self, *args, **kwargs):
        raise NotImplementedError

    def verify(self, data):
        status = http.OK
        print data['variant']
        try:
            variant = mongo.db.product_variants.find_one({
                        '_id': ObjectId(data['variant'])})
            response = {
                'message': 'OK',
                'seats': 4,
                'option': variant.price_options[0]
            }
        except Exception as e:
            response = {
                'message': 'ERROR',
                'exception': e.message,
            }
            status = http.BAD_REQUEST

        return jsonify_status_code(response, status)
