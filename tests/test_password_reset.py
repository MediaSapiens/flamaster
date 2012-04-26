from conftest import url_client, create_user, valid_user, request_context
from flask import url_for

from flamaster.app import db, app, mail


def setup_module(module):
    db.create_all()
    with app.test_request_context('/'):
        create_user()


@url_client('account.request_reset')
def test_request_reset_get(url, client):
    resp = client.get(url)
    assert resp.status_code == 200
    assert 'email' in resp.data


@url_client('account.request_reset')
def test_request_reset_post_404(url, client):
    data = {'email': 'no_test@example.com'}
    resp = client.post(url, data=data)
    assert resp.status_code == 404


@url_client('account.request_reset')
def test_request_reset_post_302(url, client):
    with mail.record_messages() as outbox:
        data = {'email': 'test@example.com'}
        resp = client.post(url, data=data)

        assert len(outbox) == 1
        assert valid_user().create_token().replace(
            '\n', '%0A').replace(
            '=', '%3D').replace(
            '$', '%24') in outbox[0].body

    assert resp.status_code == 302


@url_client('account.confirm_reset', token='not_valid_token')
def test_not_valid_token_403(url, client):
    resp = client.get(url)
    assert resp.status_code == 403


@request_context
def test_valid_token():
    url = url_for('account.confirm_reset', token=valid_user().create_token())
    with app.test_client() as c:
        resp = c.get(url)
        assert resp.status_code == 200

# ?????
@request_context
def test_valid_token_not_valid_data():
    url = url_for('account.confirm_reset', token=valid_user().create_token())
    with app.test_client() as c:
        resp = c.post(url, data={'password': '111', 'password_confirm': ''})
        assert resp.status_code == 200
        assert 'blank value is not allowed' in resp.data

        resp = c.post(url, data={'password': '', 'password_confirm': '111'})
        assert resp.status_code == 200
        assert 'blank value is not allowed' in resp.data

        resp = c.post(url, data={'password': '111', 'password_confirm': '222'})
        assert resp.status_code == 200
        assert 'Not equal' in resp.data

        resp = c.post(url, data={'password': '111', 'password_confirm': '111'})
        assert resp.status_code == 302


def teardown_module(module):
    db.drop_all()
