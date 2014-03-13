# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from collections import Mapping
import datetime
import os

from flask import abort
from flask.ext.mail import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from mongoengine import StringField, ListField, EmailField, DateTimeField

import settings
from flamaster.core import http
from flamaster.extensions import mail, mongo
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


class FileOpen(object):
    length = 0

    def __init__(self, name, parent):
        self.name = str(name)
        self.grid_id = self.name
        self.parent = parent

        self._set_contetn_type()
        self.filepath = os.path.join(settings.BASE_DIR, self.name)

        if settings.USE_S3:
            key = Key(self.parent.bucket)
            key.key = self.name
            key.set_acl('public-read')
            key.get_contents_to_filename(self.filepath)

        if not os.path.exists(self.filepath):
            abort(http.NOT_FOUND)

        self.file = open(self.filepath, 'rb')

    def __getattr__(self, attr):
        return getattr(self.file, attr)

    def __exit__(self):
        self.file.close()
        if settings.USE_S3:
            os.remove(self.filepath)

    def _set_contetn_type(self):
        self.content_type = 'image/gif'
        self.contentType = self.content_type

    @property
    def uploadDate(self):
        return self.parent.updated_at


class FileModel(mongo.Document, DocumentMixin):
    """ File storage for s3 and local file system """

    name = StringField()
    created_at = mongo.DateTimeField()
    updated_at = mongo.DateTimeField(default=datetime.datetime.now)

    if settings.USE_S3:
        s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                               settings.AWS_SECRET_ACCESS_KEY)
        bucket = s3.get_bucket(settings.S3_UPLOAD_BUCKET_NAME)
        bucket.set_acl('public-read')

    def __unicode__(self):
        return self.name

    @property
    def image(self):
        return FileOpen(self.pk, parent=self)

    @property
    def path(self):
        if settings.USE_S3:
            return 'http://{host}/{file_id}'.format(
                        host=settings.S3_UPLOAD_BUCKET_NAME,
                        file_id=self.pk)

        else:
            return settings.rel('tmpupload', str(self.pk))

    @classmethod
    def store(cls, image, content_type, **kwargs):
        instance = cls(name=kwargs.get('name'))
        instance.save()

        if settings.USE_S3:
            file_format = instance.name.split('.')[-1].lower()

            key = cls.bucket.new_key(instance.pk)
            key.set_contents_from_file(image)

            # Set ticket files as private
            key.set_acl('public-read' if file_format != 'pdf' else 'private')

        else:
            filepath = os.path.join(settings.BASE_DIR, str(instance.pk))
            with open(filepath, 'wb') as f:
                f.write(image.read())

        return instance

    @classmethod
    def create(cls, image, content_type, **kwargs):
        return cls.store(image, content_type, **kwargs)

    @classmethod
    def get(cls, id):
        instance = cls.objects(pk=id).get_or_404()
        return instance.image

    @classmethod
    def find_one(cls, **kwargs):
        return cls.objects(**kwargs).first()

    def get_file(self):
        return self.image

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()

        self.updated_at = datetime.datetime.now()
        return super(FileModel, self).save(*args, **kwargs)

