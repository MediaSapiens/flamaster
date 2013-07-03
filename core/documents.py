# -*- encoding: utf-8 -*-
from __future__ import absolute_import
# from bson.errors import InvalidId
from collections import Mapping
from flask import current_app
from flask.ext.mail import Message
from flask.ext.mongoengine import Document
from flamaster.extensions import mail

from mongoengine import StringField, ListField, EmailField

from .decorators import classproperty
from .utils import plural_underscored


class BaseMixin(object):

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

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs).save()

    def update(self, **kwargs):
        instance = self._setattrs(**kwargs)
        if isinstance(self, Document):
            return instance.save()
        else:
            return instance

    def _setattrs(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k.startswith('_'):
                raise ValueError('Underscored values are not allowed')
            setattr(self, k, v)
        return self

    @classmethod
    def convert(cls, data):
        """ Create GrouponDeal instance from dict or return unchanged if
            already
            params:
            :data_dict: `dict` or `GrouponDeal`:class: instance

            returns:
            `GrouponDeal`:instance:
        """
        if isinstance(data, cls):
            return data
        elif isinstance(data, Mapping):
            return cls(**data)
        else:
            return None


class DocumentMixin(BaseMixin):
    """ Base mixin for all mongodb models
    """
    @classproperty
    def __meta__(cls):
        return {
            'collection': plural_underscored(cls.__name__)
        }


class StoredMail(DocumentMixin, Document):
    subject = StringField(required=True)
    recipients = ListField(EmailField())
    attachments = ListField()
    html_body = StringField()
    text_body = StringField()

    def send(self):
        msg = Message(self.subject, recipients=list(self.recipients),
                      body=self.text_body, html=self.html_body)
        if self.attachments:
            for file_name, file_type, file_path in self.attachments:
                with current_app.open_resource(file_path) as fp:
                    msg.attach(file_name, file_type, fp.read())
        mail.send(msg)
        self.delete()
