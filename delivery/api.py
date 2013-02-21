from __future__ import absolute_import
from flask import current_app

from flamaster.core.decorators import api_resource
from flamaster.core.resources import Resource
from flamaster.core.utils import jsonify_status_code

from werkzeug import import_string
from . import bp


@api_resource(bp, 'options', {'id': int})
class DeliveryResource(Resource):

    def get(self, id=None):
        resolved_options = {}
        for key, value in current_app.config['DELIVERY_OPTIONS'].iteritems():
            if 'default' not in value:
                resolved_options[key] = import_string(value['module'])

        items = [{key: Cls.name} for key, Cls in resolved_options.iteritems()]
        return self.__build_response(items)

    def put(self, id=None):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def delete(self, id=None):
        raise NotImplementedError()

    def __build_response(self, items):
        response = {
            'objects': items,
            'meta': None
        }
        return jsonify_status_code(response)
