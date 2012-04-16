# from __future__ import absolute_import
import base64
import random
from datetime import datetime
from time import mktime

from flask.ext import sqlalchemy
from sqlalchemy.orm import class_mapper

from flamaster.app import db, app
from flamaster.core.utils import get_hexdigest

from .signals import user_added_signal


class CRUDMixin(object):
    """ Basic CRUD mixin
    """
    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        commit and db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        commit and db.session.commit()

    def as_dict(self):
        """ method for building dictionary for model value-properties filled
            with data from mapped storage backend
        """
        return dict((c.name, getattr(self, c.name))
              for c in class_mapper(self.__class__).mapped_table.c)


class User(db.Model, CRUDMixin):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    addresses = db.relationship('Address', lazy='dynamic',
                                backref=db.backref('user', lazy='joined'),
                                cascade="all, delete, delete-orphan")
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return "<User: %r>" % self.email

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter_by(email=email.lower()).first()
        if user is not None:
            salt, hsh = user.password.split('$')
            if hsh == get_hexdigest(salt, password):
                return user
        return user

    @classmethod
    def is_unique(cls, email):
        return cls.query.filter_by(email=email).count() == 0

    @classmethod
    def validate_token(cls, token=None):
        if token is not None:
            key, hsh = token.split('$$')
            user = cls.query.filter_by(base64.decodestring(key))
            return token == user.create_token() and user
        return None

    @classmethod
    def create(cls, **kwargs):
        with sqlalchemy.models_committed.connect_to(user_added_signal,
                                                    sender=app):
            instance = cls(**kwargs).save()
        return instance.save()

    def create_token(self):
        """ creates a unique token based on user last login time and
        urlsafe encoded user key
        """
        ts_datetime = self.logged_at or self.created_at
        ts = int(mktime(ts_datetime.timetuple()))
        key = base64.encodestring(self.email)
        base = "{}{}".format(key, ts)
        salt, hsh = self.password.split('$')
        return "{}$${}".format(key, get_hexdigest(salt, base))

    def set_password(self, raw_password):
        rand_str = lambda: str(random.random())
        salt = get_hexdigest(rand_str(), rand_str())[:5]
        hsh = get_hexdigest(salt, raw_password)
        self.password = '{}${}'.format(salt, hsh)
        return self


class Address(db.Model, CRUDMixin):
    """
        representing address data for users
    """
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    apartment = db.Column(db.String(20))
    zip_code = db.Column(db.String(20))
    type = db.Column(db.Enum('billing', 'delivery', name='addr_types'),
                     nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        assert 'city' in kwargs and 'street' in kwargs
        self.type = kwargs.pop('type', 'delivery')
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return "<Address:('%s','%s')>" % (self.city, self.street)


class Role(db.Model, CRUDMixin):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', lazy='dynamic',
                            backref=db.backref('role', lazy='joined'))
