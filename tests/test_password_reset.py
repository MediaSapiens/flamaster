import urllib2

from conftest import url_client, create_user, valid_user, request_context
from flask import url_for

from flamaster.app import db, app, mail


def setup_module(module):
    db.create_all()
    with app.test_request_context('/'):
        create_user()


def teardown_module(module):
    db.session.remove()
    db.drop_all()


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
        assert urllib2.quote(valid_user().create_token()) in outbox[0].body

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


@request_context
def test_valid_token_not_valid_data():
    url = url_for('account.confirm_reset', token=valid_user().create_token())
    with app.test_client() as c:
        resp = c.post(url, data={'password': '111', 'password_confirm': ''})
        assert resp.status_code == 200
        assert "Passwords don&#39;t match" in resp.data
        resp = c.post(url, data={'password': '', 'password_confirm': '111'})
        assert resp.status_code == 200
        assert "Passwords don&#39;t match" in resp.data
        resp = c.post(url, data={'password': '111', 'password_confirm': '222'})
        assert resp.status_code == 200
        assert "Passwords don&#39;t match" in resp.data
        resp = c.post(url, data={'password': '111', 'password_confirm': '111'})
        assert resp.status_code == 302
