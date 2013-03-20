# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from flamaster.core import COUNTRY_CHOICES
from flamaster.core.decorators import multilingual
from flamaster.core.models import CRUDMixin, TreeNode, NodeMetaClass

from flamaster.extensions import db


__all__ = ['Category', 'Favorite', 'Shelf']


@multilingual
class Category(db.Model, TreeNode):
    """ Product category mixin
    """
    __metaclass__ = NodeMetaClass
    __mp_manager__ = 'mp'

    name = db.Column(db.Unicode(256))
    description = db.Column(db.UnicodeText)
    category_type = db.Column(db.String, nullable=False, default='catalog')
    order = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "{1}: <{0.id}, '{0.name}', {0.mp_depth}>".format(self,
            self.__class__.__name__)


class Country(db.Model, CRUDMixin):
    """ Model holding countries list
    """
    short = db.Column(db.Unicode(3), nullable=False, index=True)

    @property
    def name(self):
        return COUNTRY_CHOICES[self.short]


class Favorite(db.Model, CRUDMixin):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                        ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('favorites',
                                                      lazy='dynamic'))
    product_id = db.Column(db.String(255), index=True)


class Shelf(db.Model, CRUDMixin):
    """ Model to keep available products
    """
    price_option_id = db.Column(db.String(24), unique=True, index=True)
    quantity = db.Column(db.Integer, default=0)
    sold = db.Column(db.Integer, default=0)

    @classmethod
    def get_by_price_option(cls, price_option_id):
        """ Filter shelf items by price options
        """
        if not isinstance(price_option_id, basestring):
            price_option_id = str(price_option_id)
        return cls.query.filter_by(price_option_id=price_option_id)


# TODO: add favorites
# TODO: what about related products?
# TODO: m.b. need single model for producer
