# -*- encoding: utf-8 -*-
import trafaret as t

from flask import abort, request
from flask.views import MethodView


from . import http
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
            instance = self.get_object(id).update(with_reload=True, **data)
            response = self.serialize(instance)
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
        return self.get_objects().filter_by(id=id).first_or_404()

    def paginate(self, page, page_size=20, **kwargs):
        paging = self._prepare_pagination(page, page_size, **kwargs)
        items = paging['objects'].limit(page_size).offset(paging['offset'])
        return items, paging['count'], paging['last_page']

    @classmethod
    def serialize(cls, instance, include=None):
        """ Method to controls model serialization in derived classes
        :rtype : dict
        """
        return instance.as_dict(api_fields=include)


class MongoResource(ModelResource):
    """ Resource for typical views, based on mongo models
    """

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if self.model is None:
            abort(http.BAD_REQUEST)
        return self.model.query.find(kwargs)

    def get_object(self, id):
        """ Method for extracting single object for requested id regarding
            on previous filters applied
        """
        object_id = self.model._convert_mongo_id(id)
        objects = self.get_objects(_id=object_id)
        return objects.count() and objects[0] or abort(http.NOT_FOUND)

    def paginate(self, page, page_size=20, **kwargs):
        paging = self._prepare_pagination(page, page_size, **kwargs)
        items = paging['objects'].limit(page_size).skip(paging['offset'])
        return items, paging['count'], paging['last_page']
