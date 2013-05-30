from itertools import chain
import uuid
from flask import redirect, current_app
from flask.ext.babel import gettext as _
from flask.ext.social import login_failed as social_login_failed
from flask.ext.security import login_user
from flask.signals import Namespace

from werkzeug.local import LocalProxy
from flamaster.core.utils import send_email

security = LocalProxy(lambda: current_app.extensions['security'])
social = LocalProxy(lambda: current_app.extensions['social'])

user_ds = LocalProxy(lambda: security.datastore)
connection_ds = LocalProxy(lambda: social.datastore)
providers = LocalProxy(lambda: social.providers)


signals = Namespace()

billing_data_changed = signals.signal('billing-data-changed')


@social_login_failed.connect
def another_try(app, provider_id, oauth_response):
    connect_handler = providers[provider_id].connect_handler
    connection_values = connect_handler.get_connection_values(oauth_response)

    user_kwargs = {
        'first_name': connection_values['display_name'],
        'email': "{}@{}".format(connection_values['provider_user_id'],
                                connection_values['provider_id']),
        'password': uuid.uuid4().hex,
        'roles': [app.config['USER_ROLE']]
    }
    user = user_ds.find_user(email=user_kwargs['email']) or \
                user_ds.create_user(**user_kwargs)

    connection_values['user_id'] = user.id
    connection_ds.create_connection(**connection_values)
    connection_ds.commit()
    login_user(user)
    redirect('/account/')
    # app.logger.debug("I've got this shit: {}".format(connection_values))
    # TODO: write user & connection autocreation here.
    # pass


@billing_data_changed.connect
def notify_billing_changed(sender, user):
    role = security.datastore.find_role(current_app.config['ADMIN_ROLE'])
    recipients = map(lambda u: u.email, role.users)
    send_email(_('Billing data changed'), recipients,
               'billing_data_changed', user=user)
