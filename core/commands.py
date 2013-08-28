from __future__ import absolute_import

from flask import current_app
from flask.ext.script import Command, Option

from flamaster.core.indexer import index
from flamaster.extensions import db, es, mongo

from pyelasticsearch import ElasticHttpNotFoundError
# from tests.initial_data import Requirements

__all__ = ['CreateAll', 'DropAll']


class CreateAll(Command):

    def run(self):
        db.create_all()


class DropAll(Command):

    def run(self):
        db.drop_all()



# class RunTests(Command):

#     def handle(self, app, *args, **kwargs):
#         """
#         Handles the command with given app. Default behaviour is to call within
#         a test request context.
#         """
#         app.config.from_object('test_settings')
#         with app.app_context():
#             db.drop_all(app=app)
#             db.create_all(app=app)
#             reqs = Requirements()
#             reqs('user')
#             reqs('categories')
#             nose.run(argv=['-xs', 'tests'])


class IndexCommand(Command):

    def run(self, drop_index=False):
        if drop_index:
            self.drop_indexes()
        else:
            self.create_indexes()

    def drop_indexes(self):
        try:
            es.delete_index(current_app.config['INDEX_NAME'])
        except ElasticHttpNotFoundError as error:
            print error

    def create_indexes(self):
        index.reindex()

    def get_options(self):
        return (
            Option('--drop', action="store_true", dest='drop_index'),
            # Option('--no-bpython',
            #     action="store_true",
            #     dest='no_bpython',
            #     default=not(self.use_bpython))
        )
