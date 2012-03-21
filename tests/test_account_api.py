from flask import url_for
from flask.helpers import json
from flamaster.app import app, db


def setup_module(module):
    print(app)
    db.create_all()


def test_flask_invocation(flaskapp):
    with flaskapp.test_client() as c:
        resp = c.get('/')
        assert 'title' in resp.data


def test_account_api_invocation(flaskapp):
    with flaskapp.test_request_context('/'):
        sessions_url = url_for('account.sessions')
        c = flaskapp.test_client()
        resp = c.get(sessions_url)
        assert resp.content_type == 'application/json'

        json_response = json.loads(resp.data)
        assert json_response['object']['is_anonymous'] == True


def test_session_creation(flaskapp):
    with flaskapp.test_request_context('/'):
        sessions_url = url_for('account.sessions')
        with flaskapp.test_client() as c:
            resp = c.post(sessions_url,
                    data=json.dumps({'email': 'test@mail.com'}),
                    content_type='application/json')
            j_resp = json.loads(resp.data)
            assert isinstance(j_resp['object']['uid'], int)
            assert j_resp['object']['is_anonymous'] == False


def teardown_module(module):
    test_db = getattr(module, 'db', None)
    test_db and test_db.drop_all()

