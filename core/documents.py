# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from collections import Mapping
from flask.ext.mail import Message

from flamaster.extensions import mail, mongo

from mongoengine import StringField, ListField, EmailField, FileField

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
        if isinstance(self, mongo.Document):
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


class StoredMail(DocumentMixin, mongo.Document):
    subject = StringField(required=True)
    recipients = ListField(EmailField())
    attachments = ListField()
    html_body = StringField()
    text_body = StringField()

    def send(self):
        msg = Message(self.subject, recipients=list(self.recipients),
                      body=self.text_body, html=self.html_body)
        if self.attachments:
            for file_id in self.attachments:
                file_instance = FileModel.find_one(id=file_id)
                msg.attach(file_instance.name,
                           file_instance.image.contentType,
                           file_instance.image.read()
                )

        mail.send(msg)
        self.delete()


class FileModel(mongo.Document, DocumentMixin):
    """ Wrapper around MongoDB gridfs session and file storage/retrieve
        actions
    """
    image = FileField(required=True)
    name = StringField(unique=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def store(cls, image, content_type, **kwargs):
        instance = cls(name=kwargs.get('name'))
        instance.image.put(image, content_type=content_type)
        instance.save()
        return instance

    @classmethod
    def create(cls, image, content_type, **kwargs):
        return cls.store(image, content_type, **kwargs)

    @classmethod
    def get(cls, id):
        """ Get mognodb stored file by its unique identifier
        """
        instance = cls.objects(pk=id).get_or_404()
        return instance.image

    @classmethod
    def find_one(cls, **kwargs):
        return cls.objects(**kwargs).first()

    def get_file(self):
        """ Return file-like object bound to this class from the gridfs storage
        """
        return self.image
