from __future__ import absolute_import
from flamaster.core.resources import ModelResource
from flamaster.delivery.models import ProductDelivery


class ProductDeliveryResource(ModelResource):
    model = ProductDelivery

    def put(self, id=None):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def delete(self, id=None):
        raise NotImplementedError()
