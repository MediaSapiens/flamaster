from __future__ import absolute_import
from flask.ext.script import Command


class ShelfCommand(Command):
    """Rebuild shelf state from the data in price options"""

    def run(self):
        self.enshure_on_shelf()

    def enshure_on_shelf(self):
        from flamaster.product.models import Shelf, Cart
        from findevent.event.models import PriceOption

        for price_option in PriceOption.query.find():
            str_id = str(price_option.id)
            shelf_q = Shelf.get_by_price_option(price_option_id=str_id)
            ordered = Cart.query.filter_by(is_ordered=True,
                                             price_option_id=str_id).count()

            actual_quantity = price_option.quantity - ordered

            on_shelf = shelf_q.count()

            if on_shelf == 1:
                shelf_q.update({'quantity': actual_quantity})
            elif on_shelf == 0:
                Shelf.create(price_option_id=str_id, quantity=actual_quantity)
            else:
                raise RuntimeError('shelf is over capacity')
