from flask import url_for
from flask.helpers import json
from flamaster.app import db, app
from flamaster.account.models import User, Address

from conftest import url_client, login, logout, request_context


first_address = {'city': 'Kharkov',
                 'street': '23b, Sumskaya av.',
                 'apartment': '1',
                 'zip_code': '626262',
                 'type': 'billing'}


def setup_module(module):
    db.create_all()
    User.create(email='test@email.com', password='test')


# @url_client('account.address')
# def test_address_creation_success(url, client):
#     resp = client.post(url, data=json.dumps({
#                             'email': 'test@email.com',
#                             'city': 'Test_city',
#                             'street': 'Test_street',
#                             'apartment': '12',
#                             'zip_code': '121212',
#                             'type': 'billing'}),
#                         content_type='application/json')
#     j_resp = json.loads(resp.data)

#     assert isinstance(j_resp['uid'], int)
#     assert j_resp['is_anonymous'] == False
#     assert isinstance(j_resp['address_id'], int)


@url_client('account.address')
def test_address_creation_failed_unauth(url, client):
    data = first_address.copy()
    resp = client.post(url, data=json.dumps(data),
                       content_type='application/json')

    assert resp.status_code == 403


@url_client('account.address')
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


@url_client('account.address')
def test_addresses_get_failed(url, client):
    resp = client.get(url, content_type='application/json')
    assert resp.status_code == 403


@url_client('account.address')
def test_addresses_get_success(url, client):
    uid = json.loads(login(client).data)['uid']
    resp = client.get(url, content_type='application/json')

    assert json.loads(resp.data) == {}
    assert resp.status_code == 200
    logout(client, uid)


@request_context
def test_address_get_success():
    addr = Address.create(**first_address)
    addr_url = url_for('account.address', id=addr.id)
    with app.test_client() as c:

        uid = json.loads(login(c).data)['uid']
        resp = c.get(addr_url, content_type='application/json')

        # assert json.loads(resp.data) == {}
        assert resp.status_code == 200
        logout(c, uid)


def teardown_module(module):
    db.drop_all()
