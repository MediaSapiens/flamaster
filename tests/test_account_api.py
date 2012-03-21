from flask import url_for
from flask.helpers import json
from flask.ext.sqlalchemy import SQLAlchemy
from flamaster.app import app


def setup_module(module):
    test_app = getattr(module, 'app', None)
    if test_app is None:
        test_app.config.from_object('flamaster.conf.test_settings')
        db = SQLAlchemy(test_app)
        db.create_all()
        module.app = test_app
        module.db = db


def test_flask_invocation(flaskapp):
    with flaskapp.test_client() as c:
        resp = c.get('/')
        assert 'title' in resp.data


def test_account_api_invocation(flaskapp):
    with flaskapp.test_request_context('/'):
        sessions_url = url_for('account.sessions')
        c = flaskapp.test_client()
        resp = c.get(sessions_url)
        assert resp.content_type == 'application/json'

        json_response = json.loads(resp.data)
        assert json_response['object']['is_anonymous'] == True

def teardown_module(module):
    test_db = getattr(module, 'db', None)
    test_db and test_db.drop_all()

