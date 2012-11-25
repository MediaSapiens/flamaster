from flamaster.core.decorators import api_resource
from flamaster.core.resources import Resource
from flamaster.core.utils import jsonify_status_code
from . import bp


@api_resource(bp, 'deliveries', {'id': int})
class DeliveryResource(Resource):

    def get(self, id=None):
        return self.__build_response()

    def put(self, id=None):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def delete(self, id=None):
        raise NotImplementedError()

    def __build_response(self):
        response = {
            'objects': [],
            'meta': None
        }
        return jsonify_status_code(response)
