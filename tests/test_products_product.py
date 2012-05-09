# from conftest import url_client
from flamaster.app import db
from flamaster.product.models import Product

from .conftest import create_user, valid_user, url_client


product_declaration = {
    'title': 'test project',
    'teaser': "some useful teaser",
    'description': "here will comes a description for our sample product"
}


def setup_module(module):
    db.create_all()
    # with app.test_request_context('/'):
    #     create_user()


def teardown_module(model):
    db.session.remove()
    db.drop_all()


@url_client('core.index')
def test_product_creation(url, client):
    client.get(url)
    test_user = valid_user() or create_user()
    product_declaration.update({'author': test_user})
    p = Product.create(**product_declaration)

    assert p.author.id == test_user.id
    assert p.id is not None
