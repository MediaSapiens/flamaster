from flaskext.script import Command
from flamaster.app import db
from flamaster.conf import settings
from sqlalchemy import *

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
metadata = MetaData()


class CreateAll(Command):

    def run(self):
        print 'Create All'
        db.create_all()
