# -*- encoding: utf-8 -*-
import trafaret as t

from flamaster.core import http
from flamaster.core.decorators import login_required, api_resource
from flamaster.core.resources import Resource, ModelResource
from flamaster.core.utils import jsonify_status_code
from flamaster.product.models import Address

from flask import abort, request, session, g, current_app
from flask.ext.babel import lazy_gettext as _
from flask.ext.principal import AnonymousIdentity, identity_changed
from flask.ext.security import (logout_user, login_user, current_user,
                                roles_required)
from flask.ext.security.utils import verify_password
from flask.ext.security.confirmable import (confirm_email_token_status,
                                            confirm_user)
from flask.ext.security.registerable import register_user

from sqlalchemy import or_
from trafaret import extras as te

from . import bp, _security
from .models import User, Role, BankAccount

__all__ = ['SessionResource', 'ProfileResource', 'AddressResource',
           'RoleResource']


@api_resource(bp, 'sessions', {'id': None})
class SessionResource(Resource):
    validation = t.Dict({'email': t.Email}).allow_extra('*')

    def get(self, id=None):
        return jsonify_status_code(self._get_response())

    def post(self):
        data = request.json or abort(http.BAD_REQUEST)
        try:
            data = self.validation.check(data)

            if not User.is_unique(data['email']):
                raise t.DataError({'email': _("This email is already taken")})

            register_user(email=data['email'])

            response, status = self._get_response(), http.CREATED

        except t.DataError as e:
            response, status = e.as_dict(), http.BAD_REQUEST
        return jsonify_status_code(response, status)

    def put(self, id):
        data, status = request.json or abort(http.BAD_REQUEST), http.ACCEPTED
        validation = t.Dict({
            'email': t.Email,
            'password': t.String
        }).append(self._authenticate).ignore_extra('*')

        try:
            validation.check(data)
            response = self._get_response()
        except t.DataError as e:
            response, status = e.as_dict(), http.NOT_FOUND

        return jsonify_status_code(response, status)

    def delete(self, id):
        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)

        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())
        logout_user()
        return jsonify_status_code(self._get_response(), http.NO_CONTENT)

    def _authenticate(self, data_dict):
        user = _security.datastore.find_user(email=data_dict['email'])

        if verify_password(data_dict['password'], user.password):
            login_user(user)
        else:
            raise t.DataError({
                'email': "Can't find anyone with this credentials"
            })

        return data_dict

    def _get_response(self, **kwargs):
        response = {
            'id': session['id'],
            'is_anonymous': current_user.is_anonymous(),
            'uid': session.get('user_id')
        }
        response.update(kwargs)
        return response


@api_resource(bp, 'profiles', {'id': int})
class ProfileResource(ModelResource):

    validation = t.Dict({'first_name': t.String,
                         'last_name': t.String,
                         'phone': t.String}).ignore_extra('*')
    model = User

    # method_decorators = {
    #     'get': [login_required, check_permission('profile_owner')]}

    def post(self):
        raise NotImplemented('Method is not implemented')

    def put(self, id):
        # we should check for password matching if user is trying to update it
        self.validation = t.Dict({
            'first_name': t.String,
            'last_name': t.String,
            'phone': t.String,
            'role_id': t.Int,
            te.KeysSubset('password', 'confirmation'): self._cmp_pwds,
        }).append(self._change_role(id)).make_optional('role_id'). \
                                                ignore_extra('*')

        return super(ProfileResource, self).put(id)

    def _cmp_pwds(cls, value):
        """ Password changing for user
        """
        if 'password' not in value and 'confirmation' not in value:
            return value

        elif len(value['password']) < 6:
            return {'password': t.DataError(_("Passwords should be more "
                                              "than 6 symbols length"))}
        elif value['password'] != value['confirmation']:
            return {'confirmation': t.DataError(_("Passwords doesn't match"))}

        return {'password': value['password']}

    def _change_role(self, id):
        """ helper method for changing user role if specified and current_user
            has administrator rights
        """
        def wrapper(value):
            user = self.get_object(id)
            if 'role_id' in value:
                role = Role.query.get(value['role_id'])
                if user.has_role(role):
                    return value
                elif current_user.has_role(current_app.config['ADMIN_ROLE']):
                    user.roles.append(role)
                    user.save()
                    return value
                else:
                    abort(403, _('Role change not allowed'))

        return wrapper

    def get_object(self, id):
        """ overriding base get_object flow
        """
        if request.json and 'token' in request.json:
            token = request.json['token']
            expired, invalid, instance = confirm_email_token_status(token)
            confirm_user(instance)
            instance.save()
            login_user(instance, True)
        elif current_user.has_role('admin'):
            instance = User.query.get_or_404(id)
        else:
            instance = g.user

        instance is None and abort(http.NOT_FOUND)
        return instance

    def get_objects(self, *args, **kwargs):
        arguments = request.args.to_dict()
        allowed_args = ('first_name', 'last_name', 'email')
        filters = list(
                (getattr(self.model, arg).like(u'%{}%'.format(arguments[arg]))
                    for arg in arguments.iterkeys() if arg in allowed_args))
        self.model is None and abort(http.INTERNAL_ERR)
        return self.model.query.filter(or_(*filters))

    def serialize(self, instance, include=None):
        exclude = ['password']
        if g.user.is_anonymous() or instance.is_anonymous():
            return instance.as_dict(include, exclude)

        if g.user.id != instance.id or g.user.is_superuser() is False:
            exclude.append('email')

        return instance.as_dict(include, exclude)


@api_resource(bp, 'addresses', {'id': int})
class AddressResource(ModelResource):

    validation = t.Dict({'city': t.String,
                         'street': t.String,
                         'type': t.String(regex="(billing|delivery)")}) \
                    .allow_extra('*')
    model = Address

    def post(self):
        g.user.is_anonymous() and abort(http.UNAUTHORIZED)
        request.json.update({'user_id': g.user.id})
        return super(AddressResource, self).post()

    def put(self, id):
        self.validation.make_optional('apartment', 'zip_code', 'user_id')
        return super(AddressResource, self).put(id)

    def get_objects(self):
        """ Method for extraction object list query
        """
        self.model is None and abort(http.INTERNAL_ERR)
        not g.user.is_anonymous() or abort(http.UNAUTHORIZED)

        return g.user.addresses


@api_resource(bp, 'roles', {'id': int})
class RoleResource(ModelResource):

    model = Role
    validation = t.Dict({'name': t.String}).ignore_extra('*')
    decorators = [login_required]
    method_decorators = {'post': roles_required('admin'),
                         'put': roles_required('admin')}

    def delete(self, id):
        """ We forbid roles removal """
        abort(http.METHOD_NOT_ALLOWED)


@api_resource(bp, 'bank_accounts', {'id': int})
class BankAccountResource(ModelResource):
    model = BankAccount
    validation = t.Dict({
            'bank_name': t.String,
            'iban': t.String,
            'swift': t.String
    }).ignore_extra('*')
    decorators = [login_required]

    def post(self):
        status = http.CREATED
        try:
            data = self.validation.check(request.json)
            data['user_id'] = current_user.id
            response = self.model.create(**data).as_dict()
        except t.DataError as e:
            response, status = e.as_dict(), http.BAD_REQUEST

        jsonify_status_code(response, status)

    def get_object(self, id):
        instance = super(BankAccountResource, self).get_object(id)
        if instance.check_owner(current_user) or current_user.is_superuser():
            return instance
        return abort(http.UNAUTHORIZED)
