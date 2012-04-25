from flask import g, session, render_template, request_started
from flask.ext.sqlalchemy import models_committed

from flamaster.core.utils import send_email
from .models import User


__all__ = ['signal_router']


def user_created(instance):
    message_body = render_template('email_registered.html',
                                   token=instance.create_token())
    send_email(to=instance.email, body=message_body,
               subject='Please activate your account')
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


def propagate_user(app):
    if 'uid' in session:
        g.user = User.get(session['uid'])
    else:
        g.user = User(email='nobody@example.com')


request_started.connect(propagate_user)
