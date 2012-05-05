from flask import session
from flask.helpers import json
from flamaster.app import app, db
from flamaster.account.models import User

from .conftest import login, url_client


def setup_module(module):
    db.create_all()


def teardown_module(module):
    db.drop_all()


def test_flask_invocation():
    with app.test_client() as c:
        resp = c.get('/')
        assert 'title' in resp.data


@url_client('account.sessions')
def test_account_api_invocation(url, client):
    resp = client.get(url)
    json_response = json.loads(resp.data)

    assert 'id' in json_response


@url_client('account.sessions')
def test_session_creation(url, client):
    resp = client.post(url, data=json.dumps({'email': 'test@example.com'}),
                       content_type='application/json')
    j_resp = json.loads(resp.data)

    assert isinstance(j_resp['uid'], int)


@url_client('account.sessions')
def test_authorization(url, client):
    client.get(url)
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    user.set_password('test').save()

    # assert session['is_anonymous'] == True

    resp = login(client, 'test@example.com', 'test')
    j_resp = json.loads(resp.data)

    assert 'uid' in j_resp
    assert isinstance(session['uid'], long)
    assert session['is_anonymous'] == False


@url_client('account.sessions')
def test_authorization_failed(url, client):
    resp = login(client, 'test@example.com', 'test')
    assert resp.status_code == 404
    # j_resp = json.loads(resp.data)
    # assert 'email' in j_resp
    # assert session['is_anonymous'] == True
