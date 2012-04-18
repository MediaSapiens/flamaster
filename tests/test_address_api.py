from flask.helpers import json
from flamaster.app import db, app
from flamaster.account.models import Address

from conftest import url_client, login, logout, create_user


first_address = {'city': 'Kharkov',
                 'street': '23b, Sumskaya av.',
                 'apartment': '1',
                 'zip_code': '626262',
                 'type': 'billing'}

dafault_address = {'user_id': 1,
                   'city': 'Test_city',
                   'street': 'Test_street',
                   'apartment': '12',
                   'zip_code': '121212',
                   'type': 'billing'}


def setup_module(module):
    db.create_all()
    with app.test_request_context('/'):
        create_user()


@url_client('account.addresses')
def test_address_creation_failed_unauth(url, client):
    data = first_address.copy()
    resp = client.post(url, data=json.dumps(data),
                       content_type='application/json')

    assert resp.status_code == 401


@url_client('account.addresses')
def test_address_creation_failed_no_data(url, client):
    data = first_address.copy()
    del data['type'], data['city'], data['street']
    uid = json.loads(login(client).data)['uid']
    resp = client.post(url, data=json.dumps(data),
                       content_type='application/json')

    assert 'type' in json.loads(resp.data)
    assert 'city' in json.loads(resp.data)
    assert 'street' in json.loads(resp.data)
    assert resp.status_code == 400

    logout(client, uid)


@url_client('account.addresses')
def test_addresses_get_failed(url, client):
    resp = client.get(url, content_type='application/json')
    assert resp.status_code == 401


@url_client('account.addresses')
def test_addresses_get_success(url, client):
    uid = json.loads(login(client).data)['uid']
    resp = client.get(url, content_type='application/json')

    assert json.loads(resp.data) == {}
    assert resp.status_code == 200
    logout(client, uid)


@url_client('account.addresses', id=1)
def test_addresses_put_401(url, client):
    Address.create(**dafault_address)
    resp = client.put(url, content_type='application/json')
    assert resp.status_code == 401


@url_client('account.addresses', id=1)
def test_addresses_put_400(url, client):
    uid = json.loads(login(client).data)['uid']
    resp = client.put(url, content_type='application/json')

    assert resp.status_code == 400
    logout(client, uid)


@url_client('account.addresses', id=1)
def test_addresses_put_not_valid_data(url, client):
    uid = json.loads(login(client).data)['uid']
    address_data = first_address.copy()
    del address_data['city']
    resp = client.put(url, data=json.dumps(address_data),
                      content_type='application/json')

    assert resp.status_code == 400
    assert json.loads(resp.data) == {u'city': u'is required'}
    logout(client, uid)


@url_client('account.addresses', id=1)
def test_addresses_put_201(url, client):
    uid = json.loads(login(client).data)['uid']
    resp = client.put(url, data=json.dumps(first_address),
                      content_type='application/json')

    address_data = first_address.copy()
    address_data.update({'id': 1, 'user_id': uid})
    assert json.loads(resp.data) == address_data
    assert resp.status_code == 201
    logout(client, uid)


@url_client('account.addresses', id=1)
def test_addresses_delete_401(url, client):
    resp = client.delete(url, content_type='application/json')
    assert resp.status_code == 401


@url_client('account.addresses', id=1)
def test_addresses_delete_400(url, client):
    uid = json.loads(login(client).data)['uid']
    resp = client.delete(url, content_type='application/json')

    assert resp.status_code == 200
    logout(client, uid)


def teardown_module(module):
    db.drop_all()
