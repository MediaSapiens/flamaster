from __future__ import absolute_import
from flamaster.core.resources import ModelResource
from flamaster.delivery.models import ProductDelivery


class ProductDeliveryResource(ModelResource):
    model = ProductDelivery

    def get_objects(self, **kwargs):
        filters = {'variant_id': None, 'country_id': None}
        filters.update(kwargs)

        return super(ProductDeliveryResource, self).get_objects(**filters)

    def put(self, id=None):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def delete(self, id=None):
        raise NotImplementedError()
