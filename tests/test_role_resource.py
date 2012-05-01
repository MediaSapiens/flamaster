from flask import url_for, session
from flask.helpers import json
from flamaster.app import app, db
from flamaster.account.models import User

from .conftest import create_user, url_client, login#, request_context


def setup_module(module):
    db.create_all()
    with app.test_request_context('/'):
        create_user()


@url_client('account.roles')
def test_address_creation_failed_unauth(url, client):
    login(client)
    resp = client.get(url, content_type='application/json')
    assert resp.status_code == 200
    assert resp.data == {}


def teardown_module(module):
    db.drop_all()
