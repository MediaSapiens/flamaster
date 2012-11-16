# encoding: utf-8

import trafaret as t

from bson import ObjectId
from datetime import datetime
from operator import itemgetter, methodcaller

from flask import abort, request
from flask.views import MethodView, MethodViewType
from flask.ext.mongoset import signal_map
# from flask.ext.security import login_required
from sqlalchemy import event

from . import http, indexer
from .decorators import classproperty
from .utils import jsonify_status_code


class Resource(MethodView):

    method_decorators = None

    def dispatch_request(self, *args, **kwargs):
        """ Overriding MethodView dispatch call to decorate every
            method-related view-function with the method-related decorators
            declared as dictionary in the method_decorators class-value

            Sample:
            method_decorators = {
                'get': user_required,
                'post': [in_groups('manager'), check_superuser],
                'put': [owner_required],
                'delete': [owner_required]
            }
        """
        method = super(Resource, self).dispatch_request

        if self.method_decorators is None:
            return method(*args, **kwargs)

        method_decorators = self.method_decorators.get(request.method.lower())

        if method_decorators:

            if isinstance(method_decorators, (list, tuple)):
                for decorator in method_decorators:
                    method = decorator(method)

            elif getattr(method_decorators, '__call__'):
                method = method_decorators(method)

        return method(*args, **kwargs)

    def get_objects(self, *args, **kwargs):
        """abstract method, must be implemented in subclasses,
        like method for extraction objects query.
        Must returns two arguments, first is the query and
        second is an list of keys for sorting or None
        """
        raise NotImplemented('Method is not implemented')

    def _prepare_pagination(self, page=1, page_size=20, **kwargs):
        page, objects = int(page), self.get_objects(**kwargs)
        count = objects.count()
        last_page = int(count / page_size) + (count % page_size and 1)

        page = page if page < last_page else last_page
        page = page if page > 0 else 1

        offset = (page - 1) * page_size
        bound = min(page_size * page, count)
        return {'objects': objects,
                'count': count,
                'last_page': last_page,
                'offset': offset,
                'bound': bound}

    def paginate(self, page, **kwargs):
        raise NotImplemented()

    # TODO: debug all operations with a page
    # def paginate(self, page=1, page_size=20, **kwargs):
        # page = int(page)
        # objects = self.get_objects(**kwargs)
        # count = objects.count()
        # pages = int(count / page_size) + (count % page_size and 1)
        # page = page if page <= pages else pages
        # page = page > 0 and page or 1
        # offset = (page - 1) * page_size

        # if indexes:
        #     limit = min(page_size * page, count)
        #     try:
        #         items = objects.all()
        #     except AttributeError:
        #         items = objects
        #     # for mongo models pagination:
        #     if isinstance(indexes, str):
        #         if indexes == 'mongo':
        #             items[offset:limit]
        #         else:
        #             items = items.sort(indexes)[offset:limit]
        #     else:
        #         items = sorted(items,
        #             key=lambda x: indexes.index(x.id))[offset:limit]
        # else:
        #     # FIXME: page is the last one in any case
        #     items = objects.limit(page_size).offset(offset)
        # return items, count, pages

    def gen_list_response(self, page, **kwargs):
        """if response contains objects list, this method generates
        structure of response, with pagination, like:
            {'meta': {'total': total objects,
                      'pages': amount pages},
             'objects': objects list}
        """
        items, total, pages = self.paginate(page, **kwargs)
        response = {'meta': {
                        'total': total,
                        'pages': pages},
                    'objects': [self.serialize(item) for item in items]}
        return response


class ModelResource(Resource):
    """ Resource for typical views, based on sqlalchemy models
    """
    model = None
    validation = t.Dict().allow_extra('*')

    def get(self, id=None):
        if id is None:
            page = int(request.args.get('page', 1))
            response = self.gen_list_response(page=page)
        else:
            response = self.serialize(self.get_object(id))
        return jsonify_status_code(response)

    def post(self):
        status = http.CREATED
        data = request.json or abort(http.BAD_REQUEST)

        try:
            data = self.validation.check(data)
            response = self.serialize(self.model.create(**data))
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def put(self, id):
        status = http.ACCEPTED
        data = request.json or abort(http.BAD_REQUEST)

        try:
            data = self.validation.check(data)
            instance = self.get_object(id)
            response = self.serialize(instance.update(**data))
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def delete(self, id):
        self.get_object(id).delete()
        return jsonify_status_code({}, http.NO_CONTENT)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        self.model is None and abort(http.BAD_REQUEST)
        return self.model.query.filter_by(**kwargs)

    def get_object(self, id):
        """ Method for extracting single object for requested id regarding
            on previous filters applied
        """
        return self.get_objects().get_or_404(id)

    def paginate(self, page, page_size=20, **kwargs):
        paging = self._prepare_pagination(page, page_size, **kwargs)
        items = paging['objects'].limit(page_size).offset(paging['offset'])
        return items, paging['count'], paging['last_page']

    @classmethod
    def serialize(cls, instance, include=None):
        """ Method to controls model serialization in derived classes
        """
        return instance.as_dict(api_fields=include)


class MongoResource(ModelResource):
    """ Resource for typical views, based on mongo models
    """

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        self.model is None and abort(http.BAD_REQUEST)
        return self.model.query.find(**kwargs)

    def get_object(self, id):
        """ Method for extracting single object for requested id regarding
            on previous filters applied
        """
        return self.get_objects().get_or_404(ObjectId(id))

    def paginate(self, page, page_size=20, **kwargs):
        paging = self._prepare_pagination(page, page_size, **kwargs)
        items = paging['objects'].limit(page_size).skip(paging['offset'])
        return items, paging['count'], paging['last_page']


class SearchViewType(MethodViewType):
    """This metaclass implements the sphinxsearch functionality
       into ModelResource.

       Adds signals for self.model methods (insert, update, delete),
       that change model realtime search index.
       Adds index table into class.
       Adds select functionality into class.
       Adds SearchResource subclass into index_objects, to
       create sphinx.config
    """
    def __init__(cls, name, bases, dct):
        MethodViewType.__init__(cls, name, bases, dct)

        def build_attrs_list(key):
            if cls.index_fields[key] is list:
                attribute = ArrayAttribute(key)
            else:
                attribute = Attribute(key)

            return attribute

        if cls.model is not None:
            cls.make_signals()
            attrs = map(build_attrs_list, cls.index_fields)
            table_name = "{}_rt".format(cls.index_name)
            cls.index_table = Index(table_name, indexer.metadata, *attrs)
            cls.select = select(["*"], from_obj=[cls.index_table])
            index_objects.append(cls)


class SearchResource(ModelResource):
    """ModelResource with sphinxsearch functionality.

       Requires:
       :model: field came from the ModelResource, it should contain
       Model to implement search functionality.

       :index_fields: it should contain dictionary of field names
       that will be added to the search index like dictionary keys
       and types of the fileds, like values.
       Support the following attribute types:
                                    (int, float, list, str, datetime).
       By default :index_fields: is empty.

       :index_options: contains special options to insert into sphinx.conf
       By default :index_fields: is empty. Like the list of strings

       Sample:
            class UserResource(SearchResource):
                model = User
                index_fields = {'id': int, 'name': str}
                index_options = ['enable_star = 1']
    """
    __metaclass__ = SearchViewType

    index_fields = {}
    index_options = []

    @classproperty
    def index_name(cls):
        return cls.model.__tablename__

    @classmethod
    def execute(cls, query):
        return indexer.engine.execute(query)

    def get_objects(self):
        request_dict = request.args.to_dict()
        query = request_dict.get('q')
        if query:
            return self.execute_sphinx(query)
        else:
            return super(SearchResource, self).get_objects()

    def execute_sphinx(self, query):
        indexes = self.execute(self.select.match(query)).fetchall()
        indexes = map(itemgetter(0), indexes)
        query = self.model.query.filter(self.model.__table__.c.id.in_(indexes))
        return query, indexes

    @classmethod
    def after_insert(cls, mapper=None, connection=None, instance=None):
        ins = cls.index_table.insert().values(**cls.get_values(instance))
        cls.execute(ins)

    @classmethod
    def after_update(cls, mapper, connection, instance):
        result = cls.execute(cls.select.where(
            cls.index_table.c.id == instance.id)).first()
        if result:
            repl = cls.index_table.replace().values(**cls.get_values(instance))
            cls.execute(repl)
        else:
            cls.after_insert(mapper, connection, instance)

    @classmethod
    def after_delete(cls, mapper=None, connection=None, instance=None):
        delete = cls.index_table.delete().where(
                            cls.index_table.c.id == instance.id)
        cls.execute(delete)

    @classmethod
    def make_signals(cls, events=('after_insert',
                                  'after_update', 'after_delete')):
        map(lambda e_type: event.listen(cls.model, e_type,
                                        getattr(cls, e_type)), events)

    @classmethod
    def get_values(cls, instance):
        index_fields = cls.index_fields
        values = self.serialize(instance, include=index_fields.keys())
        for key, value in values.iteritems():
            if value is None:
                if index_fields[key] == str:
                    values[key] = ''
                elif index_fields[key] == list:
                    index_fields[key] = []
                else:
                    index_fields[key] = 0

            if isinstance(value, datetime):
                values[key] = value.strftime("%s")

        return values


class MongoSearchResource(SearchResource, MongoResource):
    """ MongoResource with sphinxsearch functionality, subclass of
        :class SearchResource:
    """
    conversion_map = {}

    @classproperty
    def index_name(cls):
        return cls.model.__collection__

    def execute_sphinx(self, query):
        indexes = self.execute(self.select.match(query)).fetchall()
        indexes = map(itemgetter(0), indexes)
        query = self.model.query.find({'id': {'$in': indexes}})
        return query, indexes

    @classmethod
    def make_signal(cls, sender, **kwargs):
        instance = kwargs['collection'].get(kwargs['_id'])
        call = methodcaller(kwargs['signal'], instance=instance)
        return call(cls)

    @classmethod
    def make_signals(cls):
        map(methodcaller('connect', cls.make_signal,
                         sender=cls.model.__name__), signal_map.values())

    @classmethod
    def get_values(cls, instance):
        include_fields = cls.conversion_map or cls.index_fields.keys()
        return cls.serialize(instance, include=include_fields)


# TODO: translation ?????
# TODO: favorites for user???

# class TableResource(Resource):
#     """ Resource for views based on a table, witch is mapping M2M relation
#         between users table and other object - related object.
#         requires login user.
#         The base table must have the same name as the backref to users,
#         and the first row in the base table must be ForeignKey to 'id'
#         of related object

#         Sample:
#             comments = Table('comment', db.metadata,
#                 db.Column('comment_id', db.Integer,
#                           db.ForeignKey('comments.id')),
#                 db.Column('user_id', db.Integer, db.ForeignKey('users.id')))

#             class Comment(db.Model):
#                 id = db.Column(db.Integer, primary_key=True)
#                 ...
#                 comments_by  = db.relationship('User', secondary=comments
#                                                  backref='comments')
#     """

#     table = None
#     validation = t.Dict({'objects': t.List(t.Dict({'id': t.Int}))})\
#                     .allow_extra('*')
#     method_decorators = {'post': [login_required]}

#     @property
#     def columns(self):
#         return [column.name for column in self.table.get_children()]

#     @property
#     def ref_column(self):
#         return self.table.get_children()[0]

#     def get(self):
#         return jsonify_status_code(self.gen_list_response())

#     def post(self):
#         data = request.json or abort(http.BAD_REQUEST)
#         status = http.CREATED

#         try:
#             objects = self.validation.check(data)['objects']

#             insert_data = [dict(zip(self.columns, (item['id'], g.user.id)))
#                            for item in objects]

#             response = db.engine.execute(self.table.insert(), insert_data)\
#                         .last_inserted_params()
#         except t.DataError as e:
#             status, response = http.BAD_REQUEST, e.as_dict()

#         return jsonify_status_code(response, status)

#     def delete(self, id):
#         status, response = http.NO_CONTENT, {}

#         try:
#             id = t.Int().check(id)
#             query = self.table.delete().where(self.ref_column == id)
#             db.engine.execute(query)

#         except t.DataError as e:
#             status, response = http.BAD_REQUEST, e.as_dict()

#         return jsonify_status_code(response, status)

#     def get_objects(self, **kwargs):
#         ids = kwargs.pop('ids', None)
#         query = getattr(g.user, self.table.fullname).filter_by(**kwargs)

#         if isinstance(ids, (list, tuple)):
#             query = query.filter(self.ref_column.in_(ids))

#         return query, None
