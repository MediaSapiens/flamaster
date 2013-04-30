from __future__ import absolute_import
import nose

from flask.ext.script import Command
from flamaster.extensions import db
from tests.initial_data import Requirements

__all__ = ['CreateAll', 'DropAll']


class CreateAll(Command):

    def run(self):
        db.create_all()


class DropAll(Command):

    def run(self):
        db.drop_all()


class RunTests(Command):

    def handle(self, app, *args, **kwargs):
        """
        Handles the command with given app. Default behaviour is to call within
        a test request context.
        """
        app.config.from_object('test_settings')
        with app.app_context():
            db.drop_all(app=app)
            db.create_all(app=app)
            reqs = Requirements()
            reqs('user')
            reqs('categories')
            nose.run(argv=['-xs', 'tests'])
