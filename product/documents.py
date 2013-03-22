# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import operator
from bson import ObjectId
from datetime import datetime
from decimal import Decimal
from flask.ext.mongoengine import Document
from mongoengine import PULL, EmbeddedDocument
from mongoengine.fields import (StringField, DecimalField, IntField, ListField,
                                ReferenceField, DateTimeField, MapField,
                                EmbeddedDocumentField, ObjectIdField)
from multilingual_field.fields import MultilingualStringField as MLStringField

from werkzeug.utils import import_string

from flamaster.core.documents import DocumentMixin, BaseMixin

from .exceptions import ShelfNotAvailable
from .models import Shelf
from .utils import get_cart_class
# from .signals import price_created, price_updated, price_deleted


__all__ = ['BasePriceOption', 'BaseProductVariant', 'BaseProduct',
           'ProductType']


class BasePriceOption(EmbeddedDocument, BaseMixin):
    """ A part of Products, keeps zone for hall of specified Event
    """
    id = ObjectIdField(default=ObjectId)
    name = MLStringField(required=True)
    price = DecimalField(min_value=0, default=Decimal(0))
    quantity = IntField(min_value=0, default=0)


class BaseProductVariant(Document, DocumentMixin):
    """ Keeps event variants for different venues
    """
    meta = {
        'allow_inheritance': True,
        'collection': 'product_variants'
    }

    _price_options = ListField(EmbeddedDocumentField(BasePriceOption))

    def _get_price_options(self):
        return self._price_options

    def _set_price_options(self, value):
        self._price_options = map(BasePriceOption.convert, value)

    price_options = property(_get_price_options, _set_price_options)

    def __get_prices(self):
        prices = [Decimal(0)]
        if self.price_options:
            prices = map(operator.attrgetter('price'), self.price_options)
        return prices

    @property
    def max_price(self):
        return max(self.__get_prices())

    @property
    def min_price(self):
        return min(self.__get_prices())

    @property
    def total_quantity(self):
        return sum(map(operator.attrgetter('quantity'), self.price_options))


class BaseProduct(DocumentMixin, Document):
    meta = {
        'allow_inheritance': True,
        'collection': 'products',
        'indexes': [
            'categories', 'updated_at', 'created_at', 'created_by', 'type'
        ]
    }

    sku = StringField()
    name = MLStringField(required=True)
    type = StringField(required=True)
    teaser = MLStringField()
    description = MLStringField()
    categories = ListField(IntField(), default=list, required=True)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = IntField(required=True)
    product_variants = ListField(ReferenceField(BaseProductVariant,
                                 dbref=True, reverse_delete_rule=PULL))
    accessories = ListField()

    product_variant_class = 'flamaster.product.documents.BaseProductVariant'
    price_option_class = 'flamaster.product.documents.BasePriceOption'

    def add_variant(self, **kwargs):
        """ Create and add product variant
            :param kwargs: Contains neccesray parameters required by the new
                           product variant
        """
        variant_class = import_string(self.product_variant_class)
        variant = variant_class.objects.create(**kwargs)
        self.product_variants.append(variant)
        return variant

    def get_price(self, *args, **kwargs):
        # WARNING!
        # We have another architectural problem here.
        # We get ID PriceCategory to price calculation.
        # But PriceCategory class is in the module event,
        # which should be completely encapsulated from the module product.
        raise NotImplemented('Method is not implemented')

    def add_to_shelf(self, prices):
        for price in prices:
            Shelf.create(price_category_id=str(price.id),
                         quantity=price.quantity)

    def __get_from_shelf(self, price_option_id):
        price_id = str(price_option_id)
        return Shelf.query.filter(Shelf.price_option_id == price_id,
                           Shelf.quantity > 0) \
                            .update({'quantity': Shelf.quantity - 1})

    def add_to_cart(self, customer, amount, price_option_id):
        # try:
        self.__get_from_shelf(price_option_id)

        # if shelf is None:
        #     raise ShelfNotAvailable("We can't find anything on shelf")
        # elif shelf.quantity < amount:
        #     raise ShelfNotAvailable('Total amount is {}, not so much as'
        #         ' you need ({}) '.format(shelf.quantity, amount))
        # else:
            # shelf.quantity -= amount
        product_variant_cls = import_string(self.product_variant_class)

        price_option, product_variant = product_variant_cls.get_price_option(
                                            price_option_id)
        cart = get_cart_class().create(amount, customer, self, product_variant,
                           price_option)
        return cart
        # except Exception as error:
        #     current_app.logger.debug(error.message)
        #     db.session.rollback()


class ProductType(Document, DocumentMixin):
    meta = {
        'allow_inheritance': True,
        'collection': 'product_types',
        'indexes': ['name']
    }

    name = MLStringField(required=True)
    attrs = MapField(MLStringField())
    created_at = DateTimeField(default=datetime.utcnow)
