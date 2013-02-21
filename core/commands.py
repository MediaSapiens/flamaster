from __future__ import absolute_import
from flask.ext.script import Command
from . import db

__all__ = ['CreateAll', 'DropAll']


class CreateAll(Command):

    def run(self):
        db.create_all()


class DropAll(Command):

    def run(self):
        db.drop_all()
