from flask import json

from flamaster.app import db
from flamaster.account.models import User

from .conftest import login, url_client


user_credentials = {
    'email': 'test@example.com',
    'password': 'test'
}

profile_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'phone': '+19787233551135'
}


def setup_module(module):
    db.create_all()
    User.create(**user_credentials)


def teardown_module(module):
    db.drop_all()


@url_client('account.profiles', id=1)
def test_profile_updates(url, client):
    login_resp = login(client=client, **user_credentials)

    assert login_resp.status_code == 202
    assert 1 == json.loads(login_resp.data)['uid']

    update_resp = client.put(url, data=json.dumps(profile_data),
                             content_type='application/json')

    assert update_resp.status_code == 202
    assert 'John' == json.loads(update_resp.data)['first_name']
