# from __future__ import absolute_import
from flamaster.app import db
from sqlalchemy.orm import exc as orm_exc


class User(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(15))

    addresses = db.relationship('Address', lazy='dynamic',
                                backref=db.backref('user', lazy='joined'),
                                cascade="all, delete, delete-orphan")
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.email

    def save(self, commit=True):
        db.session.add(self)
        commit and db.session.commit()
        return self

    @classmethod
    def authenticate(cls, email, password):
        return cls.query.filter_by(email=email,
                password=password).first()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()


class Address(db.Model):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    apartment = db.Column(db.String(20))
    zip_code = db.Column(db.String(20))
    type = db.Column(db.Enum('billing', 'delivery', name='addr_types'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, city, street, apartment, zip_code):
        self.city = city
        self.street = street
        self.apartment = apartment
        self.zip_code = zip_code

    def __repr__(self):
        return "<Address:('%s','%s')>" % (self.city, self.street)
        #return "<Address:('%s','%s', '%s')>" % (self.user and self.user.email \
        #                               or 'N/A', self.type)
    def save(self, commit=True):
        db.session.add(self)
        commit and db.session.commit()
        return self

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def delete(self, commit=True):
        query_obj = query_object(self)
        db.session.delete(query_obj)
        commit and db.session.commit()

    def update(self, commit=True, **kwargs):
        query_obj = query_object(self)
        for item in kwargs:
            setattr(query_obj, item, kwargs[item])
        hasattr(query_obj, 'save') and query_obj.save()
        return query_obj


class Role(db.Model):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', lazy='dynamic',
                            backref=db.backref('role', lazy='joined'))


def query_object(self):
    query_obj = db.session.query(type(self))
    params_list = list()
    for counter, item in [(1, 'apartment'), (2, 'city'), (3, 'street'),
                          (4, 'user_id'), (5, 'zip_code'), (6, 'type')]:
        if getattr(self, item):
            params_list += ['%s=:param%d' % (item, counter)]
    filter_str = ' and '.join(params_list)
    try:
        query_obj = query_obj.filter(filter_str).params(
            param1=self.apartment,
            param2=self.city,
            param3=self.street,
            param4=self.user_id,
            param5=self.zip_code,
            param6=self.type).one()
    except orm_exc.NoResultFound, e:
        return e
    return query_obj
