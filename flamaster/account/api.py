import uuid

from flask import abort, request, session
from flask.views import MethodView

import trafaret as t
from trafaret.extras import KeysSubset

from ..core import jsonify
from ..core.decorators import api_resource

from . import account
from .models import User


@api_resource(account, '/sessions/', 'sessions', {'sid': int})
class SessionResource(MethodView):

    def get(self, sid=None):
        session['is_anonymous'] = session.get('uid') and False or True
        return jsonify({'object': dict(session)})

    def post(self):
        data = request.json or abort(400)
        users_q = User.query.filter_by(email=data.get('email'))
        if users_q.count() > 0:
            return jsonify({'error': "This email is already taken"})

        elif data.get('email'):
            user = User(data['email'], None).save()
            session['uid'] = user.id
            session['is_anonymous'] = False
            return  jsonify({'object': dict(session)}, status=201)

        abort(400)

    def put(self, sid):
        data = request.json or abort(400)

        def check_user(data):
            basic = t.Dict({'email': t.Email, 'password': t.String})
            print basic.check(data)

        check_user(data)
        return jsonify({}, status=500)

    def delete(self, sid):
        pass
