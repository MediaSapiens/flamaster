from flaskext.script import Command
from flamaster.app import db


class CreateAll(Command):

    def run(self):
        db.create_all()


class DropAll(Command):

    def run(self):
        db.drop_all()
