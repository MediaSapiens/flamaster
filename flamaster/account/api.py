import uuid

from flask import abort, request, session
from flask.views import MethodView

import trafaret as t

from ..core import jsonify
from ..core.decorators import api_resource

from . import account
from .models import User


@api_resource(account, '/sessions/', 'sessions', {'id': int})
class SessionResource(MethodView):

    def get(self, id=None):
        session['is_anonymous'] = session.get('uid') and False or True
        session['id'] = session.get('id', uuid.uuid4().hex)
        return jsonify(dict(session))

    def post(self):
        data = request.json or abort(400)
        users_q = User.query.filter_by(email=data.get('email'))

        if users_q.count() > 0:
            return jsonify({'error': {
                        'email': "This email is already taken"}})

        elif data.get('email'):
            user = User(data['email'], None).save()
            session.update({'uid': user.id, 'is_anonymous': False})
            return jsonify({'object': dict(session)}, status=201)

        abort(400)

    def put(self, id):
        data = request.json or abort(400)
        resp, status = {'object': data}, 200

        validation = t.Dict({'email': t.Email, 'password':
            t.String}).append(self._check_user)

        try:
            validation.check(data)
        except t.DataError as e:
            resp, status = {'error': e.as_dict()}, 400
            session.update({'is_anonymous': True})

        return jsonify(resp, status=status)

    def delete(self, id):
        pass

    def _check_user(self, data_dict):
        user = User.authenticate(**data_dict)
        if user is None:
            raise t.DataError({'email': "There is no user matching this "
            "credentials"})
        session.update({'uid': user.id, 'is_anonymous': False})

        return data_dict
