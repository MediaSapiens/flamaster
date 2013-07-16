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
        if current_user.is_anonymous():
            cuid = session.get('customer_id')
        else:
            cuid = current_user.customer.id
        response = {
            'id': session['id'],
            'is_anonymous': current_user.is_anonymous(),
            'uid': session.get('user_id'),
            'cuid': cuid
        }
        response.update(kwargs)
        return response


class ProfileResource(ModelResource):

    validation = t.Dict({'first_name': t.String,
                         'last_name': t.String,
                         'phone': t.String}).ignore_extra('*')
    model = User

    method_decorators = {
        'put': [login_required],
    }

    def post(self):
        raise NotImplemented('Method is not implemented')

    def put(self, id):
        # we should check for password matching if user is trying to update it
        self.validation = t.Dict({
            'first_name': t.String,
            'last_name': t.String,
            'phone': t.Or(t.Null, t.String),
            'roles': self._roles_list(id),
            'avatar_id': t.Or(t.Null, t.String),
            te.KeysSubset('password', 'confirmation'): self._cmp_pwd,
        }).make_optional('roles', 'avatar_id').ignore_extra('*')

        return super(ProfileResource, self).put(id)

    def _roles_list(self, id):
        """ Check that roles list is valid and current_user
            has administrator rights
        """
        def wrapper(value):
            trafaret = t.List(t.Int)
            value = trafaret.check(value)
            roles = Role.query.filter(Role.id.in_(value)).all()

            if len(value) != len(roles):
                return t.DataError(_("Roles are invalid"))

            if current_user.is_superuser():
                return roles
            else:
              return self.get_object(id).roles

        return wrapper

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

    def get_objects(self, **kwargs):
        arguments = request.args.to_dict()
        like_args = ('first_name', 'last_name', 'email')
        filters = [getattr(self.model, arg).like(u'%{}%'.format(arguments[arg]))
                   for arg in arguments.keys() if arg in like_args]
        qs = super(ProfileResource, self).get_objects(**kwargs)
        return qs.filter(or_(*filters))

    def serialize(self, instance, include=None):
        exclude = []
        if current_user.is_anonymous() or instance.is_anonymous():
            return instance.as_dict(include)

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
        'zip_code': t.String
    }).make_optional('apartment').ignore_extra('*')

    @method_wrapper(http.CREATED)
    def post(self):
        self.validation.keys.append(t.Key('type', trafaret=t.String(regex="(billing|delivery)")))
        data = self.clean(g.request_data)
        address_type = data.pop('type')
        address = self.model.create(**data)
        self._customer.set_address(address_type, address)
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
        if 'user_id' in request.args:
            kwargs['user_id'] = request.args['user_id']

        if not current_user.is_superuser():
            kwargs['user_id'] = current_user.id

        return super(BankAccountResource, self).get_objects(**kwargs)


class CustomerResource(ModelResource, CustomerMixin):
    model = Customer

    method_decorators = {'delete': roles_required('admin')}

    validation = t.Dict({
        'first_name': t.String,
        'last_name': t.String,
        'email': t.Email,
        'phone': t.Or(t.String(allow_blank=True), t.Null),
        'notes': t.Or(t.String(allow_blank=True), t.Null),
        'sex': t.String,
        'birthdate': t.DateTime,
    }).make_optional('phone', 'notes').ignore_extra('*')

    @method_wrapper(http.ACCEPTED)
    def put(self, id):
        data = self.clean(g.request_data)
        instance = self.get_object(id).update(with_reload=True, **data)
        return self.serialize(instance)

    def get_objects(self, **kwargs):
        if current_user.is_anonymous() or not current_user.is_superuser():
            kwargs['id'] = self._customer.id
        return super(CustomerResource, self).get_objects(**kwargs)
