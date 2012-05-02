from flask.helpers import json
from flamaster.app import app, db
from flamaster.account.models import Role, User

from .conftest import create_user, url_client, login


def setup_module(module):
    db.create_all()
    with app.test_request_context('/'):
        create_user()


@url_client('account.roles', id=1)
def test_user_role(url, client):
    login(client)
    resp = client.get(url)
    assert resp.status_code == 200
    assert 'id' in resp.data
    assert 'name' in resp.data


@url_client('account.roles', id=2)
def test_role_administrator(url, client):
    login(client)
    resp = client.get(url)
    assert resp.status_code == 403
    role = Role.get_or_create(**{'name': app.config['ADMIN_ROLE']})
    User.get(1).update(**{'role': role})
    login(client)
    resp = client.get(url, data=json.dumps({'page_size': 2}),
                      content_type='application/json')
    assert resp.status_code == 200
    assert 'total' in resp.data
    assert 'name' in resp.data
    assert 'users_id' in resp.data
    resp = client.get(url, data=json.dumps({'page_size': 'xxx'}),
                      content_type='application/json')
    assert resp.status_code == 200
    resp = client.put(url, data=json.dumps({'uid': 2, 'role_id': 2}),
                      content_type='application/json')
    assert resp.status_code == 201
    assert User.get(2).role_id == 2
    resp = client.put(url, data=json.dumps({'uid': 'xxx', 'role_id': 2}),
                      content_type='application/json')
    assert resp.status_code == 400


@url_client('account.roles', id=1)
def test_role_update_failed(url, client):
    user = User.create(email='nobody@gmail.com')
    user.set_password('password').save()
    login(client, email='nobody@gmail.com', password='password')
    resp = client.put(url)
    assert resp.status_code == 403


def teardown_module(module):
    db.drop_all()
