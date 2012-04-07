from flamaster.app import db
from flamaster.account.models import Address

from conftest import request_context

first_address = {'city': 'Kharkov',
                 'street': '23b, Sumskaya av.',
                 'apartment': '1',
                 'zip_code': '626262'}

second_address = {'city': 'Kharkov',
                 'street': '23b, Sumskaya av.',
                 'apartment': '2',
                 'zip_code': '626262'}


def setup_module(module):
    db.create_all()


@request_context
def test_address_saving():
    # on start
    assert Address.query.count() == 0
    # then we created the first thing
    Address(**first_address).save()

    assert Address.query.filter_by(**first_address).count() == 1
    assert Address.query.count() == 1


# def test_create_address():
#     pre_address_count = db.session.query(Address).count()
#     assert pre_address_count == 1
#     Address.create(**second_address)
#     address = db.session.query(Address).filter_by(**second_address).count()
#     addresses_count = db.session.query(Address).count()
#     assert addresses_count == 2 and address == 1


# def test_delete_address():
#     pre_address_count = db.session.query(Address).count()
#     assert pre_address_count == 2
#     db.session.query(Address).filter_by(**first_address).one().delete()
#     address = db.session.query(Address).filter_by(**first_address).count()
#     addresses_count = db.session.query(Address).count()
#     assert addresses_count == 1 and address == 0


# def test_update_address():
#     pre_address_count = db.session.query(Address).count()
#     assert pre_address_count == 1
#     update_address = db.session.query(Address).filter_by(**second_address).one()
#     update_address.update(city='Kiev', apartment='3b')
#     address = db.session.query(Address).filter_by(
#         city='Kiev', apartment='3b').count()
#     addresses_count = db.session.query(Address).count()
#     assert addresses_count == 1 and address == 1


def teardown_module(module):
    db.drop_all()
