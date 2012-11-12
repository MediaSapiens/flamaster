from flask import g

from flamaster.core.utils import permissions

from .models import User


@permissions.register
def profile_owner(id=None):
    """ Check if profile accessed by it's owner or an superuser
    """
    if g.user.is_superuser():
        return True
    elif id:
        user = User.query.get(id)
        return user and user.id == g.user.id or False
    else:
        return False


@permissions.register
def is_superuser(*args, **kwargs):
    return g.user.is_superuser()
