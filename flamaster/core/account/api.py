from flask import jsonify
from flask.views import MethodView
from flamaster.core.utils.decorators import api_resource

from . import account


@api_resource(account, '/sessions/', 'sessions', {'sid': int})
class SessionResource(MethodView):

    def get(self, sid=None):
        if sid is None:
            return jsonify({'response': 'nothing'})
        else:
            return jsonify({'response': 'anything'})

    def post(self):
        pass

    def put(self, sid):
        pass

    def delete(self, sid):
        pass
