# -*- encoding: utf-8 -*-
from __future__ import absolute_import
# from bson.errors import InvalidId

from .decorators import classproperty
from .utils import plural_underscored


class DocumentMixin(object):
    """ Base mixin for all mongodb models
    """
    @classproperty
    def __meta__(cls):
        return {
            'collection': plural_underscored(cls.__name__),
            'allow_inheritance': True,
        }

    def as_dict(self, include=None, exclude=['password']):
        """ method for building dictionary for model value-properties filled
            with data from mapped storage backend
        """
        document_fields = self._fields.keys()

        exportable_fields = (include or []) + document_fields

        exclude = ['_ns', '_int_id', '_class'] + (exclude or [])

        exportable_fields = set(exportable_fields) - set(exclude)

        # convert undescored fields:
        result = dict()
        for field in exportable_fields:
            value = getattr(self, field)
            if hasattr(value, '__call__'):
                value = value()

            result[field] = value

        return result

    def update(self, **kwargs):
        return self.__setattrs(**kwargs).save()

    def __setattrs(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k.startswith('_'):
                raise ValueError('Underscored values are not allowed')
            setattr(self, k, v)
        return self


# class EmbeddedDocument(DocumentMixin):
#     """ Base Model to keep an instances inside of other mongodb
#         objects, adds attribute '_ns' into stored instance.
#         Doesn't need to be registered
#     """
#     __abstract__ = True

#     structure = t.Dict().allow_extra('id')

#     def __init__(self, initial=None, **kwargs):
#         if 'id' not in kwargs:
#             kwargs['id'] = ObjectId()
#         # kwargs['_ns'] = self.__collection__
#         super(EmbeddedDocument, self).__init__(initial, **kwargs)

#     @classmethod
#     def create(cls, initial=None, **kwargs):
#         return cls(initial, **kwargs)
