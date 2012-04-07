import uuid

from flask import Blueprint, abort, request, session

import trafaret as t

from flamaster.core.utils import jsonify, as_dict
from flamaster.core.decorators import api_resource
from flamaster.core.resource_base import BaseResource

from .models import User, Address


account = Blueprint('account', __name__, template_folder='templates',
                    url_prefix='/account')


@api_resource(account, '/sessions/', 'sessions', {'id': None})
class SessionResource(BaseResource):

    def get(self, id=None):
        session['is_anonymous'] = not bool(session.get('uid'))
        session['id'] = session.get('id', uuid.uuid4().hex)
        return jsonify(dict(session))

    def post(self):
        data = request.json or abort(400)
        users_q = User.query.filter_by(email=data.get('email'))

        if users_q.count() > 0:
            return jsonify({'email': "This email is already taken"})

        elif data.get('email'):
            user = User(data['email'], None).save()
            session.update({'uid': user.id, 'is_anonymous': False})
            return jsonify(dict(session), status=201)

        abort(400)

    def put(self, id):
        data, status = request.json or abort(400), 200

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
        pass

    def _authenticate(self, data_dict):
        user = User.authenticate(**data_dict)
        if user is None:
            raise t.DataError({'email': "There is no user matching this "
            "credentials"})
        session.update({'uid': user.id, 'is_anonymous': False})

        return data_dict


@api_resource(account, '/profiles/', 'profiles', {'id': int})
class ProfileResource(BaseResource):

    def get(self, id=None):
        user = User.query.filter_by(id=self.current_user).first()
        if user is None:
            abort(404)
        response = as_dict(user)
        response['password'] = ''
        return jsonify(response)

    def post(self):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass


@api_resource(account, '/address/', 'address', {'id': int})
class AddressResource(BaseResource):

    def get(self, id=None):
        if id is None:
            uid = session.get('uid') or abort(403)
            addresses = Address.query.filter_by(user_id=uid)
            response = [as_dict(addr) for addr in addresses]

        else:
            addr = Address.query.filter_by(id=id).first() or abort(404)
            response = as_dict(addr)
        return jsonify(response)

    def post(self):
        uid = session.get('uid') or abort(403)
        data = request.json or abort(400)
        data.update({'user_id': uid})
        validation = t.Dict({'city': t.String, 'street': t.String,
                            'apartment': t.String(regex='^.{,20}$'),
                            'zip_code': t.String(regex='^.{,20}$'),
                            'type': t.String(regex="(billing|delivery)"),
                            'user_id': t.Int})
        try:
            validation.check(data)
            addr = Address.create(**data)
            data, status = as_dict(addr), 201
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)

    def put(self, id):
        data, status = request.json or abort(400), 200

        validation = t.Dict({'email': t.Email, 'password':
            t.String}).append(self._authenticate)
        try:
            data = {'email': data.get('email'), 'password':
                    data.get('password')}
            validation.check(data)
            address = Address.query.filter_by(id=id).one()
            address.update(request.json)
            session['address_id'] = address.id
            data.update(session)
        except t.DataError as e:
            data, status = e.as_dict(), 404
            session.update({'is_anonymous': True})

        return jsonify(data, status=status)

    def delete(self, id):
        t.Int.check(id)
        address = Address.query.filter_by(id=id)
        address.delete()
        return jsonify({}, status=200)

    def _authenticate(self, data_dict):
        user = User.authenticate(**data_dict)
        if user is None:
            raise t.DataError({'email': "There is no user matching this "
            "credentials"})
        session.update({'uid': user.id, 'is_anonymous': False})
        return data_dict
