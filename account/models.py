# -*- encoding: utf-8 -*-
from datetime import datetime

from flask import current_app
from flask.ext.security import UserMixin, RoleMixin

from flamaster.core.models import CRUDMixin
from flamaster.extensions import db

from operator import attrgetter
from sqlalchemy.ext.hybrid import hybrid_property


class Address(db.Model, CRUDMixin):
    """ Represents address data for users
        By default model inherits id and created_at fields from the CRUDMixin
    """
    __mapper_args__ = {
        'order_by': ['country_id', 'city']
    }
    city = db.Column(db.Unicode(255), nullable=False)
    street = db.Column(db.Unicode(255), nullable=False)
    apartment = db.Column(db.Unicode(20))
    zip_code = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id',
                                                      ondelete='CASCADE',
                                                      use_alter=True,
                                                      name='fk_customer_id'))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    country = db.relationship('Country')

    def __repr__(self):
        return "<Address:('%s','%s')>" % (self.city, self.street)


user_roles = db.Table('user_roles', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'),
              primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'),
              primary_key=True),
)


class Customer(db.Model, CRUDMixin):
    sex = db.Column(db.Unicode(1), index=True)
    birthdate = db.Column(db.DateTime, index=True)
    first_name = db.Column(db.Unicode(255), default=u'')
    last_name = db.Column(db.Unicode(255), default=u'')
    email = db.Column(db.String(80), index=True)
    phone = db.Column(db.String(80), default='')
    fax = db.Column(db.String(80), default='')
    gender = db.Column(db.String(1), default='')
    company = db.Column(db.Unicode(255), default=u'')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.UnicodeText)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", backref=db.backref("customer",
                                                      uselist=False))
    addresses = db.relationship('Address', backref=db.backref('customer'),
                        primaryjoin="Address.customer_id==Customer.id",
                        cascade='all, delete', lazy='dynamic')
    billing_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id',
                        use_alter=True, name='fk_billing_address'))
    _billing_address = db.relationship("Address", cascade='all, delete',
                        primaryjoin="Customer.billing_address_id==Address.id")
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id',
                        use_alter=True, name='fk_delivery_address'))
    _delivery_address = db.relationship("Address", cascade='all, delete',
                        primaryjoin="Customer.delivery_address_id==Address.id")

    def __unicode__(self):
        return "{0.first_name} {0.last_name}".format(self)

    @property
    def __addresses_ids(self):
        return map(attrgetter('id'), self.addresses)

    def set_address(self, addr_type, value):
        """
        :param addr_type: Either `billing` or `delivery` to describe type the
                          address will be used for
        :param value:     Instance of the Address model
        """
        if value.id not in self.__addresses_ids:
            self.addresses.append(value)

        setattr(self, "{}_address_id".format(addr_type), value.id)
        return self

    @hybrid_property
    def billing_address(self):
        """ Hybrid property allowing only one billing-address per-customer
        """
        return self._billing_address

    @billing_address.setter
    def billing_address(self, value):
        """ setter for billing_address property
        """
        self.set_address('billing', value)

    @hybrid_property
    def delivery_address(self):
        """ Hybrid property allowing only one delivery_address per-customer
        """
        return self._delivery_address

    @delivery_address.setter
    def delivery_address(self, value):
        """ setter for delivery_address property
        """
        self.set_address('delivery', value)


class Role(db.Model, CRUDMixin, RoleMixin):
    """ User's role representation as datastore persists it.
        By default model inherits id and created_at fields from the CRUDMixin
    """
    name = db.Column(db.String(255), unique=True, index=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Role: %r>" % self.name

    @classmethod
    def get_or_create(cls, name=None):
        role_name = name or current_app.config['USER_ROLE']
        instance = cls.query.filter_by(name=role_name).first() or \
                        cls.create(name=role_name)

        return instance


class User(db.Model, CRUDMixin, UserMixin):
    """ User representation from the datastore view.
        By default model inherits id and created_at fields from the CRUDMixin
    """
    api_fields = ['email', 'active', 'created_at', 'logged_at',
                  'current_login_at', 'first_name', 'last_name', 'phone',
                  'billing_address']
    __mapper_args__ = {
        'order_by': ['email']
    }

    email = db.Column(db.String(80), unique=True, index=True)
    password = db.Column(db.String(512))
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    remember_token = db.Column(db.String(255), unique=True, index=True)
    authentication_token = db.Column(db.String(255), unique=True, index=True)
    confirmed_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    current_login_ip = db.Column(db.String(128))
    login_count = db.Column(db.Integer)
    avatar_id = db.Column(db.String(24))

    roles = db.relationship('Role', secondary=user_roles,
                                backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "<User: %r>" % self.email

    def __init__(self, **kwargs):
        """ User creation process, set up role for user
            :params kwargs: should contains `email`, `password` and `active`
                            flag to set up base user data
        """
        admin_role = current_app.config['ADMIN_ROLE']
        user_role = current_app.config['USER_ROLE']
        email, admins = kwargs['email'], current_app.config['ADMINS']
        # detect if user should have an admin role
        role = email in admins and admin_role or user_role
        kwargs['roles'] = [Role.get_or_create(name=role)]

        customer_args = {
            'first_name': kwargs.pop('first_name', ''),
            'last_name': kwargs.pop('last_name', ''),
            'phone': kwargs.pop('phone', ''),
            'email': kwargs['email']
        }
        self.customer = Customer(**customer_args)
        super(User, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("You should use security datastore"
                                  " 'create_user' method for this operation")

    @classmethod
    def is_unique(cls, email):
        """ uniqueness check on email property
            :params email: email to check against existing users
        """
        return cls.query.filter_by(email=email).count() == 0

    @hybrid_property
    def first_name(self):
        return self.customer and self.customer.first_name or ''

    @first_name.setter
    def first_name(self, value):
        self.customer.first_name = value

    @hybrid_property
    def last_name(self):
        return self.customer and self.customer.last_name or ''

    @last_name.setter
    def last_name(self, value):
        self.customer.last_name = value

    @hybrid_property
    def phone(self):
        return self.customer and self.customer.phone or None

    @phone.setter
    def phone(self, value):
        self.customer.phone = value

    @hybrid_property
    def addresses(self):
        return self.customer.addresses

    @addresses.setter
    def addresses(self, value):
        if not isinstance(value, list):
            value = [value]

        map(self.customer.addresses.append, value)

    @property
    def billing_address(self):
        return self.customer and self.customer.billing_address or None

    def is_superuser(self):
        """ Flag signalized that user is superuser """
        # Todo — rewrite on Principal approach
        return self.has_role(current_app.config['ADMIN_ROLE'])

    @property
    def full_name(self):
        """ User full name helper """
        full_name = " ".join([self.first_name or '', self.last_name or ''])
        return full_name.strip() or self.email

    def as_dict(self, include=None, exclude=None):
        include, exclude = exclude or [], include or []
        exclude.extend(['password', 'remember_token', 'authentication_token'])
        include.extend(['first_name', 'last_name', 'phone', 'billing_address',
                        'is_superuser', 'roles'])
        return super(User, self).as_dict(include, exclude)


class BankAccount(db.Model, CRUDMixin):
    bank_name = db.Column(db.Unicode(512))
    iban = db.Column(db.String(256))
    swift = db.Column(db.String(256))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('accounts',
                           lazy='dynamic'))

    def check_owner(self, user):
        return user.id == self.user_id


class SocialConnection(db.Model, CRUDMixin):
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('connections',
                           lazy='dynamic'), cascade='all')
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.Unicode(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)
