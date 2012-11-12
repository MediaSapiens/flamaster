# -*- encoding: utf-8 -*-

import trafaret as t

from bson import ObjectId, DBRef
from bson.errors import InvalidId

from decorators import classproperty
from flask import current_app
from flask.ext.mongoset import Model
from operator import attrgetter

from .utils import plural_underscored


class DocumentMixin(Model):
    """ Base mixin for all mongodb models
    """
    __abstract__ = True

    structure = t.Dict().allow_extra('id')

    @classproperty
    def __collection__(cls):
        return plural_underscored(cls.__name__)

    def as_dict(self, api_fields=None, exclude=['_ns', '_int_id']):
        """ Returns instance as dict in selected language
        """
        fields = api_fields or self.keys()
        fields = set(fields) - set(exclude or [])

        result = dict(zip(fields, attrgetter(*fields)(self)))
        result['id'] = result.pop('_id')
        return result

    @property
    def id(self):
        return self['_id']


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


class EmbeddedDocument(DocumentMixin):
    """ Base Model to keep an instances inside of other mongodb
        objects, adds attribute '_ns' into stored instance.
        Doesn't need to be registered
    """
    __abstract__ = True

    _fallback_lang = current_app.config.get('MONGODB_FALLBACK_LANG')

    def __init__(self, initial=None, **kwargs):
        if '_id' not in kwargs:
            kwargs['_id'] = ObjectId()
        kwargs['_ns'] = self.__collection__
        super(EmbeddedDocument, self).__init__(initial, **kwargs)

    @classmethod
    def create(cls, initial=None, **kwargs):
        return cls(initial, **kwargs)


class MongoId(t.String):
    """ Trafaret type check & convert class
    """
    def __init__(self):
        super(MongoId, self).__init__()

    def converter(self, value):
        try:
            return ObjectId(value)
        except InvalidId as e:
            self._failure(e.message)
