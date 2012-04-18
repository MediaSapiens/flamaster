import uuid

from flask import abort, request, session

import trafaret as t

from flamaster.core.utils import jsonify
from flamaster.core.decorators import api_resource
from flamaster.core.resource_base import BaseResource

from . import account
from .models import User, Address

__all__ = ['SessionResource', 'ProfileResource', 'AddressResource']


@api_resource(account, 'sessions', {'id': None})
class SessionResource(BaseResource):
    validation = t.Dict({'email': t.Email}).allow_extra('*')

    def get(self, id=None):
        session.update({'is_anonymous': not bool(self.current_user),
                        'id': session.get('id', uuid.uuid4().hex)})
        return jsonify(dict(session))

    def post(self):
        data = request.json or abort(400)
        try:
            data = self.validation.check(data)
            if User.is_unique(data['email']):
                user = User.create(email=data['email'])
                response, status = dict(session), 201
                response['uid'] = user.id
            else:
                response, status = {'email': "This email is already taken"}, 400
        except t.DataError as e:
            response, status = e.as_dict(), 400
        return jsonify(response, status=status)

    def put(self, id):
        data, status = request.json or abort(400), 202
        validation = t.Dict({'email': t.Email, 'password':
            t.String}).append(self._authenticate)
        try:
            data = {'email': data.get('email'), 'password':
                    data.get('password')}
            validation.check(data)
            data.update(session)
        except t.DataError as e:
            data, status = e.as_dict(), 404
            session.update({'is_anonymous': True})
        return jsonify(data, status=status)

    def delete(self, id):
        session['is_anonymous'] = True
        del session['uid']
        return jsonify(dict(session), status=200)

    def _authenticate(self, data_dict):
        user = User.authenticate(**data_dict)
        session.update({'uid': user.id, 'is_anonymous': False})
        return data_dict


@api_resource(account, 'profiles', {'id': int})
class ProfileResource(BaseResource):

    validation = t.Dict({'first_name': t.String, 'last_name': t.String,
                         'phone': t.String})

    def get(self, id=None):
        id == self.current_user or abort(403)
        user = User.query.get_or_404(id=self.current_user)
        return jsonify(user.as_dict())

    def post(self):
        user = User.validate_token(request.json.get('token'))
        return jsonify(user.as_dict(), status=200)

    def put(self, id):
        user = None
        if 'token' in request.json:
            user = User.validate_token(request.json['token'])
        else:
            id == self.current_user or abort(403)
            user = User.query.get_or_404(id=self.current_user)
        print 'user', user
        user or abort(404)

        data = self.__extract_keys(request.json, ['first_name', 'last_name', 'phone'])
        try:
            self.validation.check(data)
            user.update(**data)
            response, status = user.as_dict(), 202
        except t.DataError as e:
            response, status = e.as_dict(), 400

        return jsonify(response, status=status)

    def delete(self, id):
        id == self.current_user or abort(403)
        user = User.query.get_or_404(id=self.current_user)
        user.delete()
        return jsonify({}, status=200)

    def __extract_keys(self, data, keys):
        return dict(filter(lambda x: x[0] in keys, data.items()))

    def __exclude_keys(self, data, keys):
        return dict(filter(lambda x: x[0] not in keys, data.items()))


@api_resource(account, 'addresses', {'id': int})
class AddressResource(BaseResource):

    validation = t.Dict({'city': t.String,
                         'street': t.String,
                         'type': t.String(regex="(billing|delivery)")}
                         ).allow_extra('*')

    def get(self, id=None):
        uid = self.current_user or abort(401)
        if id is None:
            addresses = Address.query.filter_by(user_id=uid)
            response = [addr.as_dict() for addr in addresses]

        else:
            addr = Address.query.filter_by(id=id, user_id=uid).first() or abort(404)
            response = addr.as_dict()
        return jsonify(response)

    def post(self):
        uid = self.current_user or abort(401)
        data = request.json or abort(400)
        data.update({'user_id': uid})
        try:
            self.validation.check(data)
            addr = Address.create(**data)
            data, status = addr.as_dict(), 201
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)

    def put(self, id):
        uid = self.current_user or abort(401)
        data = request.json or abort(400)
        data.update({'user_id': uid})
        self.validation.make_optional('apartment', 'zip_code', 'user_id')
        try:
            self.validation.check(data)
            addr = Address.query.filter_by(id=id, user_id=uid).one()
            addr.update(**data)
            data, status = addr.as_dict(), 201
        except t.DataError as e:
            data, status = e.as_dict(), 400
        return jsonify(data, status=status)

    def delete(self, id):
        uid = self.current_user or abort(404)
        try:
            t.Dict({'id': t.Int}).check({'id': id})
            Address.query.filter_by(id=id, user_id=uid).delete()
            data, status = {}, 200
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)
