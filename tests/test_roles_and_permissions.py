from flask import g
from conftest import create_user, request_context, login

from flamaster.app import db, app
from flamaster.account.models import Role, User, Permissions
from flamaster.core.utils import check_permission


def setup_module(module):
    db.create_all()


def teardown_module(module):
    db.drop_all()


# @app.teardown_request
# def teardown_request(exception=None):
#     print dir(g)


@request_context
def test_save_in_user_check_permission():
    assert Role.query.all() == []
    create_user()
    role = Role.query.filter_by(name='user')
    assert role.count() == 1
    with app.test_client() as c:
        assert getattr(g, 'user', False) == False

        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None

        user.set_password('test').save()
        login(c, 'test@example.com', 'test')
