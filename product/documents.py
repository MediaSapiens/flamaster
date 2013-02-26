# -*- encoding: utf-8 -*-
from __future__ import absolute_import
import operator

from datetime import datetime
from decimal import Decimal
from flask.ext.mongoengine import (StringField, DecimalField, IntField,
                                   ListField, ReferenceField, DateTimeField,
                                   MapField)
from mongoengine import PULL
from werkzeug.utils import import_string

from flamaster.core.documents import DocumentMixin

from .exceptions import ShelfNotAvailable
from .models import Cart, Shelf
# from .signals import price_created, price_updated, price_deleted


__all__ = ['BasePriceOption', 'BaseProductVariant', 'BaseProduct',
           'ProductType']


class BasePriceOption(DocumentMixin):
    """ A part of Products, keeps zone for hall of specified Event
    """
    meta = {
        'allow_inheritance': True,
        'collection': 'prices'
    }

    name = StringField(required=True)
    price = DecimalField(min_value=0, default=Decimal(0))
    quantity = IntField(min_value=0, default=0)


class BaseProductVariant(DocumentMixin):
    """ Keeps event variants for different venues
    """
    meta = {
        'allow_inheritance': True,
        'collection': 'prices'
    }

    price_options = ListField(ReferenceField(BasePriceOption, db_ref=True,
                              reverse_delete_rule=PULL))

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


class BaseProduct(DocumentMixin):
    meta = {
        'allow_inheritance': True,
        'collection': 'prices',
        'indexes': [
            'categories', 'updated_at', 'created_at', 'created_by', 'type'
        ]
    }

    sku = StringField(unique=True)
    name = StringField(required=True)
    type = StringField(required=True)
    teaser = StringField()
    description = StringField()
    categories = ListField(IntField(), default=list, required=True)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = IntField(required=True)
    product_variants = ListField(ReferenceField(BaseProductVariant,
                                 db_ref=True, reverse_delete_rule=PULL))
    accessories = ListField()

    product_variant_class = 'flamaster.product.documents.BaseProductVariant'
    proce_option_class = 'flamaster.product.documents.BasePriceOption'
    # i18n = ['name', 'teaser', 'description']

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
        return Shelf.query.with_lockmode('update_nowait') \
                    .filter_by(price_option_id=price_id).first()

    def add_to_cart(self, customer, amount, price_option_id, service):
        # try:
        shelf = self.__get_from_shelf(price_option_id)
        if shelf is not None:
            shelf.quantity -= amount

        # if shelf is None:
        #     raise ShelfNotAvailable("We can't find anything on shelf")
        # elif shelf.quantity < amount:
        #     raise ShelfNotAvailable('Total amount is {}, not so much as'
        #         ' you need ({}) '.format(shelf.quantity, amount))
        # else:
            # shelf.quantity -= amount
        price_option_class = import_string(self.price_option_class)
        product_variant_class = import_string(self.product_variant_class)

        price_option = price_option_class.objects.get(price_option_id)

        product_variant = product_variant_class.objects(
                            price_options__in=price_option).first()

        cart = Cart.create(amount, customer, self, product_variant,
                           price_option, service)
        return cart
        # except Exception as error:
        #     current_app.logger.debug(error.message)
        #     db.session.rollback()


class ProductType(DocumentMixin):
    meta = {
        'allow_inheritance': True,
        'collection': 'prices',
        'indexes': ['name']
    }

    name = StringField(required=True)
    attrs = MapField(StringField())
    created_at = DateTimeField(default=datetime.utcnow)

    # i18n = ['attrs']
