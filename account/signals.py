import uuid
from flask import redirect
from flask.ext.social import login_failed as social_login_failed
from flask.ext.security import login_user
# from flask.ext.security import current_user

from . import _social, _security
from .models import User


# @user_confirmed.connect_via(app)
# def activate_user(user, app):
#     user.update(active=True)
#     login_user(user)


# @social_login_failed.connect_via(app)
# def create_user_for(**kwargs):
#     app.logger.debug("I've got this shit: {}".format(kwargs))
#     # TODO: write user & connection autocreation here.
#     pass


@social_login_failed.connect
def another_try(app, provider_id, oauth_response):
    connect_handler = _social.providers[provider_id].connect_handler
    connection_values = connect_handler.get_connection_values(oauth_response)

    security_ds = _security.datastore
    social_ds = _social.datastore

    user_kwargs = {
        'first_name': connection_values['display_name'],
        'email': "{}@{}".format(connection_values['provider_user_id'],
                                connection_values['provider_id']),
        'password': uuid.uuid4().hex,
        'roles': [app.config['USER_ROLE']]
    }
    user = security_ds.find_user(email=user_kwargs['email']) or \
            User.create_user(**user_kwargs)

    connection_values['user_id'] = user.id
    social_ds.create_connection(**connection_values)
    social_ds.commit()
    login_user(user)
    redirect('/account/')
    # app.logger.debug("I've got this shit: {}".format(connection_values))
    # TODO: write user & connection autocreation here.
    # pass
