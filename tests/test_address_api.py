from flask import url_for, session
from flask.helpers import json
from flamaster.app import app, db
from flamaster.account.models import User

from functools import wraps


def request_context(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.test_request_context('/'):
            return func(*args, **kwargs)
    return wrapper


def setup_module(module):
    db.create_all()


def login(client, email='test@email.com', passwd='test'):
    auth_url = url_for('account.address', id=1)
    return client.put(auth_url, content_type='application/json',
            data=json.dumps({'email': email, 'password': passwd}))


def test_flask_invocation():
    with app.test_client() as c:
        resp = c.get('/')
        assert 'title' in resp.data


@request_context
def test_address_creation():
    sessions_url = url_for('account.address')
    with app.test_client() as c:
        resp = c.post(sessions_url,
                      data=json.dumps({'email': 'test@email.com',
                                       'city': 'Test_city',
                                       'street': 'Test_street',
                                       'apartment': '12',
                                       'zip_code': '121212',
                                       'type': 'billing'}),
                content_type='application/json')
        j_resp = json.loads(resp.data)

        assert isinstance(j_resp['uid'], int)
        assert j_resp['is_anonymous'] == False
        assert isinstance(j_resp['address_id'], int)


@request_context
def test_address_get():
    sessions_url = url_for('account.address')
    with app.test_client() as c:
        resp = c.get(sessions_url, data=json.dumps({'uid': 1}),
                     content_type='application/json')
        json_response = json.loads(resp.data)

        assert 'user_id' in json_response


@request_context
def test_authorization():
    sessions_url = url_for('account.address')
    with app.test_client() as c:
        c.get(sessions_url)
        User.query.filter_by(email='test@email.com').update({'password': 'test'})
        db.session.commit()

        resp = login(c, 'test@email.com', 'test')
        j_resp = json.loads(resp.data)

        assert 'email' in j_resp
        assert isinstance(session['uid'], long)
        assert session['is_anonymous'] == False
        assert isinstance(session['address_id'], long)


def teardown_module(module):
    db.drop_all()
