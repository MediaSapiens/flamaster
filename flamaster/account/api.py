import uuid

from flask import abort, g, request, session

import trafaret as t

from flamaster.core.utils import jsonify
from flamaster.core.decorators import api_resource
from flamaster.core.resource_base import BaseResource

from . import account
from .models import User, Address, Role

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
            t.String}).ignore_extra('*').append(self._authenticate)
        try:
            validation.check(data)
            response = dict(session)
        except t.DataError as e:
            response, status = e.as_dict(), 404
            session.update({'is_anonymous': True})
        return jsonify(response, status=status)

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
                         'phone': t.String}).ignore_extra('*')

    def get(self, id=None):
        id == g.user.id or abort(403)
        return jsonify(g.user.as_dict())

    def post(self):
        user = User.validate_token(request.json.get('token'))
        return jsonify(user.as_dict(), status=200)

    def put(self, id):
        user = g.user
        if 'token' in request.json:
            user = User.validate_token(request.json['token'])
        try:
            user.update(**self.validation.check(request.json))
            response, status = user.as_dict(), 202
        except t.DataError as e:
            response, status = e.as_dict(), 400

        return jsonify(response, status=status)

    def delete(self, id):
        id == g.user.id or abort(403)
        g.user.delete()
        return jsonify({}, status=200)


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
            addr = Address.create(**self.validation.check(data))
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
            addr = Address.get_or_404(id=id)

            # ????? addr.update(**self.validation.check(data)) not valid data
            # {'city': u'Kharkov', u'apartment': {u'apartment': u'1', 'user_id': 1L, u'zip_code': u'626262'}, 'user_id': {u'apartment': u'1', 'user_id': 1L, u'zip_code': u'626262'}, 'street': u'23b, Sumskaya av.', 'type': u'billing', u'zip_code': {u'apartment': u'1', 'user_id': 1L, u'zip_code': u'626262'}}

            addr.update(**data)
            data, status = addr.as_dict(), 201
        except t.DataError as e:
            data, status = e.as_dict(), 400
        return jsonify(data, status=status)

    def delete(self, id):
        uid = self.current_user or abort(404)
        try:
            Address.query.filter_by(id=id, user_id=uid).delete()
            data, status = {}, 200
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)


@api_resource(account, 'roles', {'id': int})
class RoleResource(BaseResource):

    validation = t.Dict({'name': t.String}).allow_extra('*')

    def get(self, id=None):
        role_user = self._authenticate(id=id)
        return jsonify(role_user.as_dict())

    def post(self):
        self._authenticate()
        return jsonify({})

    def put(self, id):
        self._authenticate(id=id)
        data = request.json or abort(400)
        return self.role_update(self, id=id, **data)

    def delete(self, id):
        self._authenticate(id=id)
        return self.role_update(self, id=id, **{'name': 'deactivate'})

    def _authenticate(self, id=None):
        role_user = Role.get_or_404(g.user.role_id)
        id == role_user.id or 'administrator' == role_user.name or abort(403)
        return True

    def role_update(self, id, **kwargs):
        role = Role.get_or_404(id)
        try:
            role.update(**self.validation.check(kwargs))
            data, status = role.as_dict(), 200
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)
