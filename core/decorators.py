# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import trafaret as t
import settings

from functools import wraps

from flask import abort, request
from flask.ext.babel import get_locale

from flamaster.extensions import db
from flamaster.core.models import CRUDMixin

from sqlalchemy.ext.hybrid import hybrid_property

from . import http
from .utils import jsonify_status_code, plural_underscored


def api_resource(bp, endpoint, pk_def):
    pk = pk_def.keys()[0]
    pk_type = pk_def[pk] and pk_def[pk].__name__ or None
    # building url from the endpoint
    url = "/{}/".format(endpoint)
    collection_methods = ['GET', 'POST']
    item_methods = ['GET', 'PUT', 'DELETE']

    def wrapper(resource_class):
        resource = resource_class().as_view(endpoint)
        bp.add_url_rule(url, view_func=resource, methods=collection_methods)
        if pk_type is None:
            url_rule = "{}<{}>".format(url, pk)
        else:
            url_rule = "{}<{}:{}>".format(url, pk_type, pk)

        bp.add_url_rule(url_rule, view_func=resource, methods=item_methods)
        return resource_class

    return wrapper


def multilingual(cls):

    locale = get_locale()
    if locale is None:
        lang = unicode(settings.BABEL_DEFAULT_LOCALE)
    else:
        lang = unicode(locale.language)

    def create_property(cls, localized, columns, field):

        def getter(self):
            instance = localized.query.filter_by(id=self.id,
                                                 locale=lang).first()
            return instance and getattr(instance, field) or None

        def setter(self, value):
            from_db = localized.query.filter_by(id=self.id,
                                                locale=lang).first()

            instance = from_db or localized(parent=self, locale=lang)
            setattr(instance, field, value)
            instance.save()

        def expression(self):
            return db.Query(columns[field]) \
                .filter(localized.parent_id == self.id,
                        localized.locale == lang).as_scalar()

        setattr(cls, field, hybrid_property(getter, setter, expr=expression))

    def closure(cls):
        class_name = cls.__name__ + 'Localized'
        tablename = plural_underscored(class_name)

        if db.metadata.tables.get(tablename) is not None:
            return cls

        cls_columns = cls.__table__.get_children()
        columns = dict([(c.name, c.copy()) for c in cls_columns
                        if isinstance(c.type, (db.Unicode, db.UnicodeText))])
        localized_names = columns.keys()

        columns.update({
            'parent_id': db.Column(db.Integer,
                                   db.ForeignKey(cls.__tablename__ + '.id',
                                                 ondelete="CASCADE",
                                                 onupdate="CASCADE"),
                                   nullable=True),
            'parent': db.relationship(cls, backref='localized_ref'),
            'locale': db.Column(db.Unicode(255), default=lang, index=True)
        })

        cls_localized = type(class_name, (db.Model, CRUDMixin), columns)

        for field in localized_names:
            create_property(cls, cls_localized, columns, field)

        return cls

    return closure(cls)


def method_wrapper(http_status):
    def method_catcher(meth):
        @wraps(meth)
        def wrapper(*args):
            try:
                data = request.json or abort(http.BAD_REQUEST)
                return jsonify_status_code(meth(*args, data=data), http_status)
            except t.DataError as e:
                return jsonify_status_code(e.as_dict(), http.BAD_REQUEST)
        return wrapper
    return method_catcher


class ClassProperty(property):
    def __init__(self, method, *args, **kwargs):
        method = classmethod(method)
        return super(ClassProperty, self).__init__(method, *args, **kwargs)

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


classproperty = ClassProperty
