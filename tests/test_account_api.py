from flask import url_for
from flask.helpers import json
from flamaster.app import app, db

from functools import wraps


def request_context(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.test_request_context('/'):
            return func(*args, **kwargs)
    return wrapper


def setup_module(module):
    db.create_all()


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
                data=json.dumps({'email': 'test@mail.com'}),
                content_type='application/json')
        j_resp = json.loads(resp.data)
        assert isinstance(j_resp['object']['uid'], int)
        assert j_resp['object']['is_anonymous'] == False


@request_context
def test_authorization():
    pass


def teardown_module(module):
    test_db = getattr(module, 'db', None)
    test_db and test_db.drop_all()

