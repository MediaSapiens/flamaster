from flask.ext.sqlalchemy import models_committed
from flask.ext.mail import Mail
from .models import User


__all__ = ['signal_router']


def user_created(instance):
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
