from flask import g, url_for
from conftest import create_user, request_context, login

from flamaster.app import db, app
from flamaster.account.models import Role, User, Permissions
from flamaster.core.utils import check_permission


def setup_module(module):
    db.create_all()


def teardown_module(module):
    db.drop_all()


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
        Permissions.create(name='test_permissions')
        role = Role.get(user.role_id)
        role.permissions.append(Permissions(name='test_permissions_in_role'))
        role.save()
        login(c, 'test@example.com', 'test')
        assert getattr(g, 'user').email == 'nobody@example.com'

        c.get(url_for('account.sessions'))
        g_user = getattr(g, 'user')
        assert g_user.email == 'test@example.com'

        assert check_permission('test_permissions') == False
        assert check_permission('test_permissions_in_role') == True
