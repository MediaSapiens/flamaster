from flask.helpers import json
from flask import url_for
from flamaster.app import db, app
from flamaster.product.models import Product

from conftest import url_client, login, create_user, request_context#, logout


first_product = {'title': 'first_product',
                 'teaser': 'teaser_ product',
                 'description': 'description_product'}


def setup_module(module):
    db.create_all()
    with app.test_request_context('/'):
        create_user()


@url_client('product.products')
def test_product_create_failed_unautorized(url, client):
    resp = client.post(url)
    assert resp.status_code == 401


@url_client('product.products')
def test_product_create(url, client):
    data = first_product.copy()

    login(client)
    resp = client.post(url, content_type='application/json')
    assert resp.status_code == 400

    resp = client.post(url, data=json.dumps(data),
                       content_type='application/json')

    assert resp.status_code == 201
    assert 'slug' in json.loads(resp.data)


@url_client('product.products')
def test_product_get_failed(url, client):
    resp = client.get(url, content_type='application/json')
    assert resp.status_code == 401


@url_client('product.products')
def test_get_product(url, client):
    login(client)
    resp = client.get(url, content_type='application/json')
    assert resp.status_code == 200
    assert Product.get(1).slug in json.loads(resp.data)


@url_client('product.products', id=1)
def test_get_product_id(url, client):
    login(client)
    resp = client.get(url, content_type='application/json')
    assert resp.status_code == 200
    assert 'slug' in json.loads(resp.data)


def teardown_module(module):
    db.drop_all()
