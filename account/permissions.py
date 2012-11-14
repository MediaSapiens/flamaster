# -*- encoding: utf-8 -*-
from flask import g
from flamaster.core.utils import permissions

from . import _security


@permissions.register
def profile_owner(user_id=None):
    """ Check if profile accessed by it's owner or an superuser
    """
    if g.user.is_superuser():
        return True
    elif user_id:
        user = _security.datastore.find_user(id=user_id)
        return user and user.id == g.user.id or False
    else:
        return False


@permissions.register
def is_superuser(*args, **kwargs):
    return g.user.is_superuser()
