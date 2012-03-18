from flask import abort, jsonify, request, session
from flask.views import MethodView

from ..core.decorators import api_resource


from . import account
from .models import User


@api_resource(account, '/sessions/', 'sessions', {'sid': int})
class SessionResource(MethodView):

    def get(self, sid=None):
        session['is_anonymous'] = True
        if session.get('uid') is not None:
            session['is_anonymous'] = True
        return jsonify(session)

    def post(self):
        data = request.json or abort(400)
        users_q = User.query.filter_by(email=data.get('email'))
        if users_q.count() > 0:
            user = users_q.first()
            print dir(user)

        elif data.get('email'):
            user = User(data['email'], None).save()
            session['uid'] = user.id
            return  jsonify({'status': 'created'}), 201

        # here we need to validate data

        return jsonify({'status': 'updated'}), 200

    def put(self, sid):
        pass

    def delete(self, sid):
        pass
