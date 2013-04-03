# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t
from trafaret import extras as te

from flask import abort, request, session, current_app, g
from flask.ext.babel import lazy_gettext as _
from flask.ext.principal import AnonymousIdentity, identity_changed
from flask.ext.security import (logout_user, login_user, current_user,
                                roles_required, login_required)
from flask.ext.security.utils import verify_password, encrypt_password
from flask.ext.security.confirmable import (confirm_email_token_status,
                                            confirm_user)
from flask.ext.security.registerable import register_user

from werkzeug.local import LocalProxy

from sqlalchemy import or_

from flamaster.core import http
from flamaster.core.decorators import method_wrapper
from flamaster.core.resources import Resource, ModelResource
from flamaster.core.utils import jsonify_status_code

from .models import User, Role, BankAccount, Address, Customer

__all__ = ['SessionResource', 'ProfileResource', 'RoleResource']

security = LocalProxy(lambda: current_app.extensions['security'])


class CustomerMixin(object):

    @property
    def _customer(self):
        if current_user.is_anonymous():
            customer_id = session.get('customer_id')
            if customer_id is None:
                abort(http.BAD_REQUEST)
            customer = Customer.query.get_or_404(customer_id)
        else:
            customer = current_user.customer

        return customer


class SessionResource(Resource):
    validation = t.Dict({
        'email': t.Email,
        'password': t.Or(t.String(allow_blank=True), t.Null)
    }).make_optional('password').ignore_extra('*')

    def get(self, id=None):
        return jsonify_status_code(self._get_response())

    @method_wrapper(http.CREATED)
    def post(self):
        data = self.clean(g.request_json)

        if not User.is_unique(data['email']):
            raise t.DataError({'email': _("This email is already taken")})

        register_user(email=data['email'], password=data.get('password', '*'))
        return self._get_response()

    @method_wrapper(http.ACCEPTED)
    def put(self, id):
        cleaned_data = self.clean(g.request_data)
        self._authenticate(cleaned_data)
        return self._get_response()

    def delete(self, id):
        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)

        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())
        logout_user()
        return jsonify_status_code(self._get_response(), http.NO_CONTENT)

    def clean(self, data_dict):
        return self.validation.check(data_dict)

    def _authenticate(self, data_dict):
        user = security.datastore.find_user(email=data_dict['email'])

        if verify_password(data_dict.get('password'), user.password):
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
            'avatar_id': t.Or(t.Null, t.String),
            te.KeysSubset('password', 'confirmation'): self._cmp_pwd,
        }).append(self._change_role(id)).make_optional('role_id', 'avatar_id'). \
                                                ignore_extra('*')

        return super(ProfileResource, self).put(id)

    def _cmp_pwd(self, value):
        password, confirmation = (value.pop('password', None),
                                  value.pop('confirmation', None))
        if password:
            if len(password) < 6:
                return t.DataError({'password': _("Passwords should be more than 6 symbols length")})
            if password != confirmation:
                return t.DataError({'confirmation': _("Passwords doesn't match")})
            value['password'] = encrypt_password(password)
        return value

    def _change_role(self, id):
        """ helper method for changing user role if specified and current_user
            has administrator rights
        """
        def wrapper(value):
            user = self.get_object(id)
            if 'role_id' in value:
                role = Role.query.get_or_404(value['role_id'])
                if user.has_role(role):
                    return value
                elif current_user.is_superuser():
                    user.roles.append(role)
                    return value
                else:
                    abort(403, _('Role change not allowed'))
            return value
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
        elif current_user.is_superuser():
            instance = User.query.get_or_404(id)
        else:
            instance = current_user

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
        include = ['is_superuser']
        exclude = ['password']
        if current_user.is_anonymous() or instance.is_anonymous():
            return instance.as_dict(include, exclude)

        if current_user.id != instance.id or not current_user.is_superuser():
            exclude.append('email')

        return instance.as_dict(include, exclude)


class AddressResource(ModelResource, CustomerMixin):
    model = Address
    validation = t.Dict({
        'country_id': t.Int,
        'apartment': t.Or(t.String(allow_blank=True), t.Null),
        'city': t.String,
        'street': t.String,
        'type': t.String(regex="(billing|delivery)"),
        'zip_code': t.String
    }).make_optional('apartment').ignore_extra('*')

    @method_wrapper(http.CREATED)
    def post(self):
        data = self.clean(g.request_data)
        address_type = data.pop('type')
        address = self.model.create(**data)
        self._customer.set_address(address_type, address).save()
        return self.serialize(address)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if current_user.is_anonymous() or not current_user.is_superuser():
            kwargs['customer_id'] = self._customer.id

        return super(AddressResource, self).get_objects(**kwargs)


class RoleResource(ModelResource):

    model = Role
    validation = t.Dict({'name': t.String}).ignore_extra('*')
    decorators = [login_required]
    method_decorators = {'post': roles_required('admin'),
                         'put': roles_required('admin')}

    def delete(self, id):
        """ We forbid roles removal """
        abort(http.METHOD_NOT_ALLOWED)


class BankAccountResource(ModelResource):
    model = BankAccount
    validation = t.Dict({
            'bank_name': t.String,
            'iban': t.String,
            'swift': t.String
    }).ignore_extra('*')
    decorators = [login_required]

    @method_wrapper(http.CREATED)
    def post(self):
        data = self.clean(g.request_data)
        data['user_id'] = current_user.id
        return self.serialize(self.model.create(**data))

    def get_object(self, id):
        instance = super(BankAccountResource, self).get_object(id)
        if instance.check_owner(current_user) or current_user.is_superuser():
            return instance
        return abort(http.UNAUTHORIZED)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if self.model is None:
            abort(http.BAD_REQUEST)
        if 'user_id' in request.args:
            kwargs['user_id'] = request.args['user_id']

        if not current_user.is_superuser():
            kwargs['user_id'] = current_user.id

        return self.model.query.filter_by(**kwargs)


class CustomerResource(ModelResource, CustomerMixin):
    model = Customer

    method_decorators = {'delete': roles_required('admin')}

    validation = t.Dict({
        'first_name': t.String,
        'last_name': t.String,
        'email': t.Email,
        'phone': t.String(allow_blank=True),
        'notes': t.Or(t.String(allow_blank=True), t.Null),
    }).make_optional('phone', 'notes').ignore_extra('*')

    @method_wrapper(http.ACCEPTED)
    def put(self, id):
        data = self.clean(g.request_data)
        instance = self.get_object(id).update(with_reload=True, **data)
        return self.serialize(instance)

    def get_objects(self, **kwargs):
        if not current_user.is_superuser():
            kwargs['id'] = self._customer.id
        return super(CustomerResource, self).get_objects(**kwargs)
