from flaskext.script import Command
from flamaster.app import db
from flamaster.conf import settings


class CreateAll(Command):

    def run(self):
        print 'Create All'
        db.create_all()


class DropAll(Command):

    def run(self):
        db.drop_all()
