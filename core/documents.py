# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t

from bson import ObjectId, DBRef
# from bson.errors import InvalidId

from flask import current_app
from flask.ext.mongoset import Model

from operator import attrgetter

from .decorators import classproperty
from .utils import plural_underscored


class DocumentMixin(Model):
    """ Base mixin for all mongodb models
    """
    __abstract__ = True

    @classproperty
    def __collection__(cls):
        return plural_underscored(cls.__name__)

    @classmethod
    def _convert_mongo_id(cls, value):
        if isinstance(value, basestring):
            return ObjectId(value)
        elif isinstance(value, ObjectId):
            return value
        else:
            raise TypeError("value should be either subclass of basestring"
                            " or an instance of bson.ObjectId")

    def as_dict(self, api_fields=None, exclude=None):
        """ Returns instance as dict in selected language
        """
        exclude_by_default = ['_ns', '_int_id', '_class']

        if exclude is not None:
            exclude_by_default.extend(exclude)

        fields = api_fields or self.keys()
        fields = set(fields) - set(exclude_by_default)
        values = []
        for field in fields:
            try:
                value = attrgetter(field)(self)
            except AttributeError:
                value = None
            values.append(value)
        result = dict(zip(fields, values))

        if '_id' in result:
            result['id'] = result.pop('_id')
        return result


class IdDocument(DocumentMixin):
    """ Base Model for mongodb models with autoicremented id
    """
    __abstract__ = True

    inc_id = True
    indexes = ['_int_id']


class Document(DocumentMixin):
    """ Base Model for mongodb models without autoicremented id
    """
    __abstract__ = True
    inc_id = False

    @property
    def db_ref(self):
        """ Helper method for DBRef construction """
        return DBRef(self.__collection__, self.id)

    def id():
        """The id property."""

        def fget(self):
            return self['_id']

        def fset(self, value):
            self['_id'] = value

        return locals()
    id = property(**id())


class EmbeddedDocument(DocumentMixin):
    """ Base Model to keep an instances inside of other mongodb
        objects, adds attribute '_ns' into stored instance.
        Doesn't need to be registered
    """
    __abstract__ = True

    _fallback_lang = current_app.config.get('MONGODB_FALLBACK_LANG')

    structure = t.Dict().allow_extra('id')

    def __init__(self, initial=None, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = ObjectId()
        # kwargs['_ns'] = self.__collection__
        super(EmbeddedDocument, self).__init__(initial, **kwargs)

    @classmethod
    def create(cls, initial=None, **kwargs):
        return cls(initial, **kwargs)
