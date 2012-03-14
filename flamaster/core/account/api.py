from flask import abort, jsonify, request, session
from flask.views import MethodView
from flamaster.core.utils.decorators import api_resource

from . import account


@api_resource(account, '/sessions/', 'sessions', {'sid': int})
class SessionResource(MethodView):

    def get(self, sid=None):
        session['is_anonymous'] = True
        if session.get('uid') is not None:
            session['is_anonymous'] = True
        return jsonify(session)

    def post(self):
        data = request.json or abort(400)
        print data
        return jsonify({'status': 'updated'})

    def put(self, sid):
        pass

    def delete(self, sid):
        pass
