from flask.ext.sqlalchemy import models_committed

from flamaster.core.utils import send_email
from .models import User


__all__ = ['signal_router']


def user_created(instance):
    send_email(to=instance.email,
               subject='', body='')
    return 'user created'


signal_map = {
    'insert': {
        User: user_created,
    },
}


def signal_router(sender, changes):
    for change in changes:
        obj, kind = change
        try:
            signal_map[kind][obj.__class__](obj)
        except KeyError as e:
            pass


models_committed.connect(signal_router)
