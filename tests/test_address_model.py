from flamaster.app import app, db


def setup_module(module):
    db.create_all()


def teardown_module(module):
    test_db = getattr(module, 'db', None)
    test_db and test_db.drop_all()
