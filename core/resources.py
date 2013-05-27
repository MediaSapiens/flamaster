# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t

from flask import abort, request, current_app, g
from flask.views import MethodView

from mongoengine.base import ValidationError

from . import http
from flamaster.core.decorators import method_wrapper
from .utils import jsonify_status_code


class Resource(MethodView):

    method_decorators = None
    filters_map = t.Dict().make_optional('*').ignore_extra('*')
    filters_map_default = True
    page_size = None

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

    def _prepare_pagination(self, **kwargs):
        if self.filters_map_default:
            try:
                self.filter_args = self.clean_args(request.args)
                kwargs.update(self.filter_args)
            except t.DataError as err:
                current_app.logger.info("Error in filters: %s", err.as_dict())

        page = kwargs.pop('page', 1)
        args_page_size = kwargs.pop('page_size', 20)
        page_size = self.page_size or args_page_size

        objects = self.get_objects(**kwargs)
        count = objects.count()
        last_page = int(count / page_size) + (count % page_size and 1)

        page = page if page < last_page else last_page
        page = page if page > 0 else 1

        offset = (page - 1) * page_size
        bound = min(page_size * page, count)
        return {
            'bound': bound,
            'count': count,
            'last_page': last_page,
            'objects': objects,
            'offset': offset,
            'page': page,
            'page_size': page_size
        }

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

    def gen_list_response(self, **kwargs):
        """if response contains objects list, this method generates
        structure of response, with pagination, like:
            {'meta': {'total': total objects,
                      'pages': amount pages},
             'objects': objects list}
        """
        # Processing fiters passed through the request.args

        items, total, pages, quantity = self.paginate(**kwargs)
        response = {'meta': {
                        'total': total,
                        'pages': pages,
                        'quantity': quantity},
                    'objects': [self.serialize(item) for item in items]}
        return response

    def clean(self, data):
        """
        Clean and normalize passed data
        :param data:
        :return: cleaned and normalized data
        """
        raise NotImplemented('Method is not implemented')

    def clean_args(self, request_args):
        # pagination support
        if not filter(lambda k: k.name == 'page', self.filters_map.keys):
            page = t.Key('page', default=1)
            page.set_trafaret(t.Int(gt=0))
            # filter set processing
            self.filters_map.keys.append(page)
        if not filter(lambda k: k.name == 'page_size', self.filters_map.keys):
            page_size = t.Key('page_size', default=20)
            page_size.set_trafaret(t.Int(gt=0))
            # filter set processing
            self.filters_map.keys.append(page_size)
        return self.filters_map.check(request_args.copy())


class ModelResource(Resource):
    """ Resource for typical views, based on sqlalchemy models
    """
    model = None
    validation = t.Dict().allow_extra('*')

    def clean(self, data):
        return self.validation.check(data)

    def get(self, id=None):
        status = http.OK
        try:
            if id is None:
                response = self.gen_list_response()
            else:
                response = self.serialize(self.get_object(id))
        except t.DataError as err:
            response, status = err.as_dict(), http.BAD_REQUEST
        return jsonify_status_code(response, status)

    @method_wrapper(http.CREATED)
    def post(self):
        data = self.clean(g.request_data)
        return self.serialize(self.model.create(**data))

    @method_wrapper(http.ACCEPTED)
    def put(self, id):
        data = self.clean(g.request_data)
        instance = self.get_object(id).update(**data)
        return self.serialize(instance)

    def delete(self, id):
        status = http.OK
        try:
            self.get_object(id).delete()
            response = {}
        except t.DataError as err:
            response, status = err.as_dict(), http.BAD_REQUEST
        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if self.model is None:
            abort(http.BAD_REQUEST)
        return self.model.query.filter_by(**kwargs)

    def get_object(self, id):
        """ Method for extracting single object for requested id regarding
            on previous filters applied
        """
        return self.get_objects(id=id).first_or_404()

    def paginate(self, **kwargs):
        paging = self._prepare_pagination(**kwargs)
        items = paging['objects'].limit(paging['page_size']) \
                    .offset(paging['offset'])
        return items, paging['count'], paging['last_page'], paging['page_size']

    @classmethod
    def serialize(cls, instance, include=None):
        """ Method to controls model serialization in derived classes
        :rtype : dict
        """
        return instance.as_dict(include=include)


class MongoResource(ModelResource):
    """ Resource for typical views, based on mongo models
    """

    def post(self):
        status = http.CREATED
        data = request.json or abort(http.BAD_REQUEST)

        try:
            data = self.clean(data)
            response = self.serialize(self.model.objects.create(**data))
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()
        except ValidationError as e:
            status, response = http.BAD_REQUEST, e.to_dict()

        return jsonify_status_code(response, status)

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        if self.model is None:
            abort(http.BAD_REQUEST)
        return self.model.objects(**kwargs)

    def get_object(self, id):
        """ Method for extracting single object for requested id regarding
            on previous filters applied
        """
        return self.get_objects(pk=id).get_or_404()

    def paginate(self, **kwargs):
        paging = self._prepare_pagination(**kwargs)
        pager = paging['objects'].paginate(paging['page'], paging['page_size'])
        return (pager.items, paging['count'], paging['last_page'],
                paging['page_size'])
