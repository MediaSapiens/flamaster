from __future__ import absolute_import
from operator import attrgetter
from flamaster.core.models import CRUDMixin
from flamaster.extensions import db


class ProductDelivery(db.Model, CRUDMixin):
    variant_id = db.Column(db.String(255), nullable=False, index=True)
    cost = db.Column(db.Numeric(precision=18, scale=2))

    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'),
                           nullable=False)
    country = db.relationship('Country')

    @classmethod
    def collect_delivery_options(cls, order):
        variant_ids = map(attrgetter('product_variant_id'), order.goods)
        country_filtered = cls.query.filter_by(
                                country_id=order.delivery_country_id)
        by_variant = country_filtered.filter(cls.variant_id.in_(variant_ids))
        return by_variant
