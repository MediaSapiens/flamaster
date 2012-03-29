# from __future__ import absolute_import
from flamaster.app import db


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
        if commit:
            db.session.commit()
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
        return "<Address:('%s','%s', '%s')>" % (self.user and self.user.email \
                                                or 'N/A', self.type)

    def create(self, commit=True):
        db.session.add(self)
        commit and db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()

    def update(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self


class Role(db.Model):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', lazy='dynamic',
                            backref=db.backref('role', lazy='joined'))
