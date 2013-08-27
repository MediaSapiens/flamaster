from __future__ import absolute_import
from operator import attrgetter
from flamaster.core.models import CRUDMixin
from flamaster.extensions import db


class ProductDelivery(db.Model, CRUDMixin):
    delivery_type = db.Column(db.String(128))
    variant_id = db.Column(db.String(255), nullable=True, index=True)
    cost = db.Column(db.Numeric(precision=18, scale=2))

    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'),
                           nullable=True)
    country = db.relationship('Country')

    __table_args__ = (db.UniqueConstraint('delivery_type', 'variant_id',
                                          'country_id',
                                          name='uq_type_variant_country'),)