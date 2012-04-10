# import flask
import os
from functools import wraps
from flask import url_for
from flask.helpers import json

from flamaster.app import app


os.environ['TESTING'] = 'True'


def request_context(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.test_request_context('/'):
            return func(*args, **kwargs)
    return wrapper


def login(client, email='test@email.com', password='test'):
    auth_url = url_for('account.sessions', id=1)
    return client.put(auth_url, content_type='application/json',
            data=json.dumps({'email': email, 'password': password}))


def logout(client, uid=1):
    auth_url = url_for('account.sessions', id=uid)
    return client.delete(auth_url)


def url_client(endpoint, **url_kwargs):
    """ Helper decorator for an address resource invocation
    """
    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            with app.test_request_context('/'):
                with app.test_client() as c:
                    url_path = url_for(endpoint, **url_kwargs)
                    kwargs.update({'url': url_path, 'client': c})
                    response = func(*args, **kwargs)
            return response
        return wrapper
    return decorate
