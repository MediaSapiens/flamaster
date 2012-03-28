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


def login(email, passwd, client):
    auth_url = url_for('account.sessions', sid=1)
    return client.put(auth_url, content_type='application/json',
            data=json.dumps({'email': 'test@email.com', 'password': 'test'}))


def test_flask_invocation():
    with app.test_client() as c:
        resp = c.get('/')
        assert 'title' in resp.data


@request_context
def test_account_api_invocation():
    sessions_url = url_for('account.sessions')
    c = app.test_client()
    resp = c.get(sessions_url)
    assert resp.content_type == 'application/json'

    json_response = json.loads(resp.data)
    assert json_response['object']['is_anonymous'] == True


@request_context
def test_session_creation():
    sessions_url = url_for('account.sessions')
    with app.test_client() as c:
        resp = c.post(sessions_url,
                data=json.dumps({'email': 'test@email.com'}),
                content_type='application/json')
        j_resp = json.loads(resp.data)

        assert isinstance(j_resp['object']['uid'], int)
        assert j_resp['object']['is_anonymous'] == False


@request_context
def test_authorization():
    sessions_url = url_for('account.sessions')
    with app.test_client() as c:
        c.get(sessions_url)
        User.query.filter_by(email='test@email.com').update({'password':
            'test'})
        db.session.commit()

        assert session['is_anonymous'] == True

        resp = login('test@email.com', 'test', c)
        j_resp = json.loads(resp.data)

        assert 'email' in j_resp['object']
        assert isinstance(session['uid'], long)
        assert session['is_anonymous'] == False


@request_context
def test_authorization_failed():
    with app.test_client() as c:
        resp = login('test@email.com', 'pass', c)
        j_resp = json.loads(resp.data)
        assert 'error' in j_resp
        assert 'email' in j_resp['error']
        assert session['is_anonymous'] == True

def teardown_module(module):
    db.drop_all()
