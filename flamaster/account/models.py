# from __future__ import absolute_import
from flamaster.app import db
from datetime import datetime
from time import mktime
import random
from .utils import get_hexdigest


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


class User(db.Model, CRUDMixin):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    last_login = db.Column(db.DateTime)

    addresses = db.relationship('Address', lazy='dynamic',
                                backref=db.backref('user', lazy='joined'),
                                cascade="all, delete, delete-orphan")
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.email

    @classmethod
    def authenticate(cls, email, password):
        return cls.query.filter_by(email=email,
                password=password).first()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update_login_time(self):
        self.last_login = datetime.utcnow()
        self.save()
        return self

    def create_token(self):
        ts_datetime = self.last_login
        ts = int(mktime(ts_datetime.timetuple()))
        base = "{}{}".format(self.key.urlsafe(), ts)
        algo, salt, pass_hash = self.password.split('$')
        return "{}$${}".format(self.key.urlsafe(), get_hexdigest(algo, salt, base))

    @classmethod
    def validate_token(cls, token):
        if token is not None:
            key_safe, hsh = token.split('$$')
            user = cls.query.filter_by().one()
            return token == user.create_token() and user
        return False

    @classmethod
    def check_password(cls, email, password):
        user = cls.query.filter_by(email=email).one()
        if user is None:
            return False
        algo, salt, hsh = user.password.split('$')
        if hsh == get_hexdigest(algo, salt, password):
            return user
        return False

    def set_password(self, raw_password):
        algo = 'sha1'
        rand_str = lambda: str(random.random())
        salt = get_hexdigest(algo, rand_str(), rand_str())[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '{}${}${}'.format(algo, salt, hsh)
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
