"""
    .. py:module:: account

    Account `flask.Blueprint` holds everything about accounting, profiles, etc.
"""
from __future__ import absolute_import
from flask import Blueprint
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.social import SQLAlchemyConnectionDatastore

from flamaster.core.utils import add_api_rule
from flamaster.extensions import db

from .models import User, Role, SocialConnection


__all__ = ['models', 'signals']

user_ds = SQLAlchemyUserDatastore(db, User, Role)
connection_ds = SQLAlchemyConnectionDatastore(db, SocialConnection)

bp = Blueprint('account', __name__, url_prefix='/account')


def add_resource(endpoint, pk_def, import_name):
    return add_api_rule(bp, endpoint, pk_def,
                        'flamaster.account.api.{}'.format(import_name))


add_resource('addresses', {'id': int}, 'AddressResource')
add_resource('bank_accounts', {'id': int}, 'BankAccountResource')
add_resource('customers', {'id': int}, 'CustomerResource')
add_resource('profiles', {'id': int}, 'ProfileResource')
add_resource('roles', {'id': int}, 'RoleResource')
add_resource('sessions', {'id': None}, 'SessionResource')

from flamaster.account import signals
