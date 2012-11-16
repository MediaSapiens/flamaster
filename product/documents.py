# -*- encoding: utf-8 -*-
import operator
import trafaret as t

from blinker import Namespace
from bson import DBRef
from datetime import datetime
from flask import current_app

from flamaster.core.documents import Document, MongoId

from . import db, mongo
from .exceptions import ShelfNotAvailable
from .models import Cart, Shelf


__all__ = ['price_created', 'price_updated', 'price_deleted',
           'BasePriceOption', 'BaseProductVariant', 'BaseProduct']

signals = Namespace()
price_created = signals.signal('price_created')
price_updated = signals.signal('price_updated')
price_deleted = signals.signal('price_deleted')


class BasePriceOption(Document):
    """ A part of Products, keeps zone for hall of specified Event
    """
    __abstract__ = True
    __collection__ = 'prices'

    structure = t.Dict({
        'name': t.String,
        'price': t.Float,
        'product_variant_id': MongoId,
        'quantity': t.Int,
    })

    required_fields = ['price', 'product_variant_id']

    @classmethod
    def create(cls, **kwargs):
        """ Kwargs are: name, price, product_variant_id, amount"""
        instance = cls(**kwargs)
        instance['_id'] = instance.save()
        price_created.send(instance)
        return instance

    def update(self, **kwargs):
        """"""
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.save()
        price_updated.send(self)
        return self

    def delete(self):
        price_deleted.send(self)
        return super(BasePriceOption, self).delete()


class BaseProductVariant(Document):
    """ Keeps event variants for different venues
    """
    __abstract__ = True
    __collection__ = 'product_variants'

    structure = t.Dict({
        'price_options': t.List[t.Type(DBRef)],
    })

    def __get_prices(self):
        prices = [0]
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


class BaseProduct(Document):
    __abstract__ = True
    __collection__ = 'products'

    structure = t.Dict({
        'sku': t.String,
        'name': t.String,
        'type': t.String,
        'teaser': t.String,
        'description': t.String,
        # 'producer': t.Int,
        'categories': t.List[t.Int],
        'updated_at': t.Any,
        'created_by': t.Int,
        'product_variants': t.List[t.Type(DBRef)],
        'accessories': t.List[t.Type(Document) | t.Type(DBRef)],
        t.Key('created_at', default=datetime.utcnow): t.Any
    })

    required_fields = ['name', 'type', 'categories', 'created_by']
    i18n = ['name', 'teaser', 'description']
    indexes = ['id', 'categories', ('updated_at', -1), ('created_at', -1),
               'created_by', 'type']

    def add_variant(self, **kwargs):
        """ Create and add product variant
            :param kwargs: Contains neccesray parameters required by the new
                           product variant
        """
        option = BaseProductVariant.create(**kwargs)
        self.update({
            '$push': {'product_variants': option.db_ref},
        })
        return option

    def get_price(self, *args, **kwargs):
        # WARNING!
        # We have another architectural problem here.
        # We get ID PriceCategory to price calculation.
        # But PriceCategory class is in the module event,
        # which should be completely encapsulated from the module product.
        raise NotImplemented('Method is not implemented')

    # def add_to_shelf(self, prices):
    #     for price in prices:
    #         Shelf.create(price_category_id=str(price.id),
    #                      quantity=price.quantity)

    def __get_from_shelf(self, price_option):
        price_id = str(price_option.id)
        return Shelf.query.with_lockmode('update_nowait') \
                    .filter_by(price_option_id=price_id).first()

    def add_to_cart(self, customer, amount, price_option_id):
        try:
            shelf = self.__get_from_shelf(price_option_id)

            if shelf is None:
                raise ShelfNotAvailable("We can't find anything on shelf")
            elif shelf.quantity < amount:
                raise ShelfNotAvailable('Total amount is {}, not so much as'
                    ' you need ({}) '.format(shelf.quantity, amount))
            else:
                shelf.quantity -= amount
                price_opt = mongo.db.prices.find_one({'_id': price_option_id})

                product_variant = mongo.db.product_variants.find_one({
                                    'price_options': price_opt.ref})

                cart = Cart.create(amount, customer_id, self, product_variant,
                                   price_opt)
                return cart
        except (InternalError, OperationalError) as error:
            current_app.logger.debug(error.message)
            db.session.rollback()


@mongo.register
class ProductType(Document):

    structure = t.Dict({
        'name': t.String,
        'attrs': t.Mapping(t.String, t.String),
        t.Key('created_at', default=datetime.utcnow): t.Any
    })

    i18n = ['attrs']
    indexes = ['name']
