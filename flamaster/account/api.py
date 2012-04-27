import uuid

from flask import abort, g, request, session
from flamaster.app import db, app

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
            addr = Address.query.filter_by(id=id, user_id=uid).first_or_404()
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
        uid = self.current_user or abort(403)
        data = request.json or abort(400)
        data.update({'user_id': uid})
        self.validation.make_optional('apartment', 'zip_code', 'user_id')
        try:
            addr = Address.query.get_or_404(id)
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

    validation = t.Dict({'uid': t.Int})

    def get(self, id=None):
        role = g.user.role
        role_dict = role.as_dict()
        if id == g.user.role and app.config['ADMIN_ROLE'] != g.user.role.name:
            return jsonify(role_dict)

        role.name == app.config['ADMIN_ROLE'] or abort(403)
        users = User.query.filter_by(role_id=role.id).all()
        try:
            page_size = t.Dict({'page_size': t.Int}).check(
                request.json)['page_size']
        except t.DataError:
            page_size = app.config['DEFAULT_PAGE_SIZE']

        role_dict.update({'total': len(users), 'users': users[:page_size]})
        return jsonify(role_dict.as_dict())

    def put(self, id):
        g.user.role.name == app.config['ADMIN_ROLE'] or abort(403)
        try:
            data = t.Dict({'uid': t.Int, 'role_id': t.Int}).check(
                request.json)
            status = 201
        except t.DataError as e:
            data, status = e.as_dict(), 400

        user = User.get(data['uid']).update(role_id=data['role_id'])
        data = user.as_dict()
        return jsonify(data, status=status)

    # def post(self):
    #     self._authenticate()
    #     return jsonify({})

    # def delete(self, id):
    #     self._authenticate(id=id)
    #     return self.role_update(self, **{'name': 'deactivate', 'id': id})
