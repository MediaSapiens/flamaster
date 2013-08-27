from __future__ import absolute_import
from flamaster.core.decorators import api_resource
from flamaster.core.resources import Resource
from werkzeug import import_string
from . import bp


@api_resource(bp, 'options', {'id': int})
class DeliveryResource(Resource):

    def get(self, id=None):
        pass

    def put(self, id=None):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def delete(self, id=None):
        raise NotImplementedError()
