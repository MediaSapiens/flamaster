# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t

from flamaster.core import http
from flamaster.core.decorators import method_wrapper
from flamaster.core.resources import ModelResource

from .helpers import resolve_parent
from .models import Category, Country


__all__ = ['CategoryResource', 'CountryResource']


class CategoryResource(ModelResource):
    page_size = 10000
    model = Category

    validation = t.Dict({
        'name': t.String,
        'description': t.String,
        'category_type': t.String,
        'parent_id': t.Int | t.Null,
        'order': t.Int,
    }).append(resolve_parent).make_optional('parent_id', 'order') \
        .ignore_extra('*')

    filters_map = t.Dict({
        'parent_id': t.Int(gt=0)
    }).make_optional('parent_id').ignore_extra('*')


class CountryResource(ModelResource):
    model = Country
    page_size = 1000

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def put(self, id, data):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def post(self, data):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def delete(self, id, data):
        return ''

    @classmethod
    def serialize(cls, instance):
        """ Method to controls model serialization in derived classes
        :rtype : dict
        """
        return instance.as_dict(include=['id', 'short', 'name'])

